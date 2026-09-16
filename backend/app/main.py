from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .config import settings
from .db import Base, engine, get_db
from .engine import ACTION_SEED, PEOPLE, SCENARIO, SIGNAL_SEED, build_graph, conflict_rows, intelligence
from .models import Action, Alert, Audit, Message, ProjectMeta, Signal, Stakeholder
from .schemas import (
    AlertRequest,
    CaptureRequest,
    HealthResponse,
    IntelligenceResult,
    ProjectResponse,
    StakeholderUpdate,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Evidence-first coordination intelligence for architecture, interior design and construction projects.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def as_dict(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


def log(db: Session, event: str, entity: str, entity_id: str, detail: str) -> None:
    db.add(Audit(id=uuid.uuid4().hex[:12], event=event, entity=entity, entity_id=entity_id, detail=detail))
    db.commit()


def seed(db: Session, force: bool = False) -> None:
    existing = db.scalar(select(ProjectMeta).where(ProjectMeta.id == "riverside"))
    if existing and not force and settings.seed_demo:
        return
    for model in [Audit, Alert, Action, Signal, Message, Stakeholder, ProjectMeta]:
        db.execute(delete(model))
    db.add(ProjectMeta(id="riverside", name="Riverside Residence", code="RS-24", demo_mode=True))
    for person in PEOPLE:
        db.add(Stakeholder(**person))
    for message in SCENARIO:
        db.add(Message(**message))
    for signal in SIGNAL_SEED:
        db.add(Signal(**signal))
    for action in ACTION_SEED:
        db.add(Action(**action))
    db.commit()
    log(db, "demo_seeded", "project", "riverside", "Seeded the AS-01 Riverside Residence coordination scenario.")


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        seed(db)
    finally:
        db.close()
    yield


app.router.lifespan_context = lifespan


def rows(db: Session, model, order_col=None, limit=300):
    query = select(model)
    if order_col is not None:
        query = query.order_by(order_col)
    return [as_dict(item) for item in db.scalars(query.limit(limit)).all()]


def dynamic_brief(signals: list[dict], actions: list[dict], conflicts: list[dict]) -> dict:
    active = [signal for signal in signals if signal["status"] != "DISMISSED"]
    critical = [signal for signal in active if signal["severity"] == "CRITICAL"]
    approvals = [signal for signal in active if signal["type"] == "APPROVAL" and signal["status"] != "CONFIRMED"]
    open_actions = [action for action in actions if action["status"] != "DONE"]

    if critical:
        headline = f"{len(critical)} critical coordination issue{'s' if len(critical) != 1 else ''} need attention."
    elif open_actions:
        headline = f"{len(open_actions)} coordination action{'s' if len(open_actions) != 1 else ''} remain open."
    else:
        headline = "No unresolved high-severity coordination issue is currently visible."

    items = []
    for signal in sorted(active, key=lambda x: (x["severity"] != "CRITICAL", x["severity"] != "HIGH"))[:3]:
        items.append(f"{signal['title']}: {signal['action']}")
    if conflicts:
        items.append(f"Resolve {len(conflicts)} detected consistency exception{'s' if len(conflicts) != 1 else ''} in project memory.")
    if not items:
        items.append("Capture the next project update to keep coordination state current.")

    recommendation = " → ".join(
        [
            "Review critical signals" if critical else "Review open signals",
            "resolve approval gates" if approvals else "validate dependencies",
            "confirm next owner actions",
        ]
    )
    return {"headline": headline, "items": items, "recommendation": recommendation}


def project_state(db: Session) -> dict:
    messages = rows(db, Message, Message.created_at)
    signals = rows(db, Signal, Signal.created_at)
    actions = rows(db, Action, Action.created_at)
    alerts = rows(db, Alert, Alert.created_at)
    audit = rows(db, Audit, Audit.ts, 250)
    people = rows(db, Stakeholder, Stakeholder.name)
    conflicts = conflict_rows(messages)

    active_signals = [s for s in signals if s["status"] != "DISMISSED"]
    critical = sum(s["severity"] == "CRITICAL" for s in active_signals)
    blockers = sum(s["type"] == "BLOCKER" for s in active_signals)
    approvals = sum(s["type"] == "APPROVAL" and s["status"] != "CONFIRMED" for s in active_signals)
    done = sum(a["status"] == "DONE" for a in actions)
    unresolved = sum(c["severity"] in ("HIGH", "CRITICAL") for c in conflicts)

    readiness = max(8, min(100, 100 - critical * 12 - blockers * 8 - approvals * 9 - unresolved * 10 + done * 4))
    risk = min(99, critical * 18 + blockers * 12 + approvals * 8 + unresolved * 16)
    project = {
        "name": "Riverside Residence",
        "code": "RS-24",
        "health": "AT RISK" if risk >= 40 else "STABLE",
        "readiness": readiness,
        "risk": risk,
        "channels": len({m["channel"] for m in messages}),
        "last_ingested": messages[-1]["time_label"] if messages else "--",
        "demo_mode": settings.seed_demo,
    }
    metrics = {
        "signals": len(signals),
        "open_blockers": blockers,
        "approval_gates": approvals,
        "critical": critical,
        "conflicts": unresolved,
        "alerts": len(alerts),
        "source_coverage": "100%",
    }
    return {
        "project": project,
        "people": people,
        "messages": messages,
        "signals": signals,
        "actions": actions,
        "alerts": alerts,
        "audit": audit[-100:],
        "conflicts": conflicts,
        "graph": build_graph(signals),
        "metrics": metrics,
        "brief": dynamic_brief(signals, actions, conflicts),
    }


@app.get("/api/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(select(ProjectMeta).limit(1))
        db_status = "connected"
    except Exception:
        db_status = "unavailable"
    return {
        "ok": True,
        "service": settings.app_name,
        "version": settings.version,
        "database": db_status,
        "engine": "provider-first intelligence + deterministic evidence fallback",
        "provider_configured": bool(settings.llm_api_key and settings.llm_base_url),
    }


@app.get("/api/project", response_model=ProjectResponse)
def project(db: Session = Depends(get_db)):
    return project_state(db)


@app.get("/api/intelligence/examples")
def examples():
    return {"messages": SCENARIO}


@app.get("/api/impact/{signal_id}")
def impact(signal_id: str, db: Session = Depends(get_db)):
    signal = db.get(Signal, signal_id)
    if not signal:
        raise HTTPException(404, "Signal not found")
    from .engine import build_impact
    return build_impact(as_dict(signal), rows(db, Message, Message.created_at))


@app.post("/api/intelligence/preview", response_model=IntelligenceResult)
def preview(body: CaptureRequest):
    return intelligence(body.text)


@app.post("/api/messages")
def capture(body: CaptureRequest, db: Session = Depends(get_db)):
    result = intelligence(body.text)
    message_id = "m" + uuid.uuid4().hex[:8]
    tag = str(result.get("intent", "CONTEXT")).split(" · ")[0]
    db.add(
        Message(
            id=message_id,
            channel=body.channel,
            sender=body.sender,
            time_label=datetime.now(timezone.utc).strftime("%H:%M UTC"),
            text=body.text,
            tag=tag[:40],
        )
    )
    owner_hint = result.get("owner_hint") or "Project Manager"
    created_actions = 0
    for item in result.get("signals", []):
        signal_type = item.get("type", "CONTEXT")
        severity = item.get("severity", "MEDIUM")
        action_text = {
            "BLOCKER": "Hold affected work until the blocker is clarified.",
            "APPROVAL": "Route for explicit approval before dependent release.",
            "CHANGE": "Confirm the current revision and broadcast the change.",
            "IMPACT": "Review downstream dependencies and affected owners.",
            "SUPPLY": "Route the supply exception to the decision owner.",
            "ACTION": "Review and confirm the proposed next step.",
        }.get(signal_type, "Review the captured context.")
        if result.get("next_actions"):
            action_text = str(result["next_actions"][0])[:500]
        signal_id = "s" + uuid.uuid4().hex[:8]
        db.add(
            Signal(
                id=signal_id,
                type=signal_type,
                severity=severity,
                title=str(item.get("title", "Coordination signal"))[:240],
                detail=str(item.get("reason", "Generated from captured project evidence."))[:2000],
                source_ids=message_id,
                owner=str(owner_hint)[:200],
                confidence=int(result.get("confidence", 80)),
                status="NEEDS_REVIEW",
                impact="Generated from the newly captured project update and should be validated against downstream work.",
                why="The recommendation is grounded in the captured note and remains behind human review.",
                action=action_text,
            )
        )
        if signal_type in {"BLOCKER", "APPROVAL", "CHANGE", "IMPACT", "SUPPLY"}:
            db.add(
                Action(
                    id="a" + uuid.uuid4().hex[:8],
                    priority="P0" if severity == "CRITICAL" else "P1",
                    title=action_text[:240],
                    owner=str(owner_hint)[:160],
                    due="Next coordination review",
                    status="OPEN",
                    reason=f"Created from {signal_type.lower()} signal: {item.get('title', 'signal')}.",
                    source_ids=message_id,
                )
            )
            created_actions += 1
    db.add(
        Audit(
            id=uuid.uuid4().hex[:12],
            event="message_captured",
            entity="message",
            entity_id=message_id,
            detail=f"{body.channel}: {len(result.get('signals', []))} signals and {created_actions} owner actions proposed by the intelligence pipeline.",
        )
    )
    db.commit()
    return {"message_id": message_id, "intelligence": result, "project": project_state(db)}


@app.post("/api/actions/{action_id}/confirm")
def confirm_action(action_id: str, db: Session = Depends(get_db)):
    action = db.get(Action, action_id)
    if not action:
        raise HTTPException(404, "Action not found")
    action.status = "DONE"
    db.add(Audit(id=uuid.uuid4().hex[:12], event="action_confirmed", entity="action", entity_id=action_id, detail="Human confirmed the recommended next action."))
    db.commit()
    return project_state(db)


@app.post("/api/signals/{signal_id}/decision/{decision}")
def decision(signal_id: str, decision: str, db: Session = Depends(get_db)):
    if decision not in ("confirm", "dismiss"):
        raise HTTPException(400, "Decision must be confirm or dismiss")
    signal = db.get(Signal, signal_id)
    if not signal:
        raise HTTPException(404, "Signal not found")
    signal.status = "CONFIRMED" if decision == "confirm" else "DISMISSED"
    db.add(Audit(id=uuid.uuid4().hex[:12], event=f"signal_{decision}", entity="signal", entity_id=signal_id, detail=f"Signal marked {signal.status.lower()} by human review."))
    db.commit()
    return project_state(db)


@app.post("/api/signals/{signal_id}/route")
def route_signal(signal_id: str, body: AlertRequest, db: Session = Depends(get_db)):
    if not db.get(Signal, signal_id):
        raise HTTPException(404, "Signal not found")
    alert_id = "al" + uuid.uuid4().hex[:8]
    db.add(Alert(id=alert_id, signal_id=signal_id, recipient=body.recipient, channel=body.channel, status="QUEUED"))
    db.add(Audit(id=uuid.uuid4().hex[:12], event="coordination_alert_queued", entity="signal", entity_id=signal_id, detail=f"Alert queued to {body.recipient} via {body.channel}. External delivery is intentionally adapter-ready for the prototype."))
    db.commit()
    return project_state(db)


@app.put("/api/stakeholders/{stakeholder_id}")
def update_stakeholder(stakeholder_id: str, body: StakeholderUpdate, db: Session = Depends(get_db)):
    person = db.get(Stakeholder, stakeholder_id)
    if not person:
        raise HTTPException(404, "Stakeholder not found")
    person.role = body.role
    person.focus = body.focus
    person.status = body.status
    db.add(Audit(id=uuid.uuid4().hex[:12], event="stakeholder_updated", entity="stakeholder", entity_id=stakeholder_id, detail=f"Role/focus/status updated for {person.name}."))
    db.commit()
    return project_state(db)


@app.post("/api/intelligence/refresh")
def refresh(db: Session = Depends(get_db)):
    db.add(Audit(id=uuid.uuid4().hex[:12], event="intelligence_refreshed", entity="project", entity_id="riverside", detail="Recomputed coordination state across the live project-memory dataset."))
    db.commit()
    return project_state(db)


@app.post("/api/demo/reset")
def reset(db: Session = Depends(get_db)):
    seed(db, True)
    return project_state(db)


frontend_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
