"""Coordination intelligence for ThreadPilot.

The provider LLM is always attempted first when configured. The deterministic
local engine is the reliability fallback so the demo remains usable offline.
The seeded AS-01 scenario is data, not the primary inference mechanism.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any

import httpx

from .config import settings

SCENARIO = [
    {"id":"m1","channel":"WhatsApp","sender":"MEP Consultant","time_label":"09:12","text":"For the master bathroom ceiling, the previous 80mm drop conflicts with the sprinkler branch. Need confirmation against A-305 Rev 05 before we issue the MEP section.","tag":"TECHNICAL"},
    {"id":"m2","channel":"Email","sender":"Architect","time_label":"09:26","text":"Please refer to A-305 Rev 04 for the ceiling detail. Rev 05 is uploaded to the project folder.","tag":"VERSION"},
    {"id":"m3","channel":"Site","sender":"Site Team","time_label":"10:03","text":"Contractor is ready to close gypsum but needs clarification. We are holding this area to avoid rework.","tag":"BLOCKER"},
    {"id":"m4","channel":"Client","sender":"Client","time_label":"10:18","text":"Approved overall, except the master bathroom. Please send the visual before final sign-off.","tag":"APPROVAL"},
    {"id":"m5","channel":"Supplier","sender":"Stone Supplier","time_label":"10:41","text":"Shade 312 is unavailable this week. Shade 318 is available now, pending designer approval.","tag":"SUPPLY"},
    {"id":"m6","channel":"Drawings","sender":"Document Control","time_label":"10:52","text":"A-305 Rev 05 uploaded. Revision supersedes Rev 04. Change cloud highlights ceiling drop and bathroom coordination detail.","tag":"CHANGE"},
]

PEOPLE = [
    {"id":"p1","name":"Architect","role":"Design owner","focus":"Decisions + drawing release","initials":"AR","status":"ACTIVE"},
    {"id":"p2","name":"MEP Consultant","role":"Services","focus":"Technical coordination","initials":"ME","status":"ACTIVE"},
    {"id":"p3","name":"Interior Designer","role":"Materials","focus":"Finish approvals","initials":"ID","status":"ACTIVE"},
    {"id":"p4","name":"Project Manager","role":"Coordination","focus":"Sequence + release","initials":"PM","status":"ACTIVE"},
    {"id":"p5","name":"Contractor","role":"Execution","focus":"Workface delivery","initials":"CO","status":"ACTIVE"},
    {"id":"p6","name":"Client","role":"Approval","focus":"Final decisions","initials":"CL","status":"ACTIVE"},
    {"id":"p7","name":"Supplier","role":"Procurement","focus":"Availability + alternatives","initials":"SU","status":"ACTIVE"},
]

SIGNAL_SEED = [
    {"id":"s1","type":"CHANGE","severity":"HIGH","title":"A-305 Rev 05 supersedes Rev 04","detail":"The current drawing set changes the master-bathroom ceiling coordination detail.","source_ids":"m2,m6","owner":"Architect + Document Control","confidence":99,"status":"CONFIRMED","impact":"Any team working from Rev 04 risks acting on superseded information.","why":"Document Control explicitly says Rev 05 supersedes Rev 04, while the prior email still references Rev 04.","action":"Broadcast Rev 05 as the sole execution reference."},
    {"id":"s2","type":"BLOCKER","severity":"CRITICAL","title":"Gypsum close-out is intentionally on hold","detail":"Site work is paused until the ceiling question is clarified.","source_ids":"m1,m3","owner":"Site Team","confidence":97,"status":"CONFIRMED","impact":"Programme risk is already active because the workface cannot safely close.","why":"Site says the area is being held to avoid rework and requests clarification.","action":"Keep the workface on hold until MEP confirms the ceiling detail."},
    {"id":"s3","type":"APPROVAL","severity":"HIGH","title":"Master bathroom is the last client approval gate","detail":"Overall approval is complete except for the master bathroom visual.","source_ids":"m4","owner":"Architect","confidence":98,"status":"NEEDS_REVIEW","impact":"Final sign-off and downstream release remain dependent on one unresolved client decision.","why":"Client explicitly excludes the master bathroom from approval and requests a visual.","action":"Send the bathroom visual and request explicit sign-off."},
    {"id":"s4","type":"IMPACT","severity":"CRITICAL","title":"Ceiling revision propagates into MEP and site","detail":"The 80mm ceiling drop conflicts with the sprinkler branch and blocks the MEP section.","source_ids":"m1,m6","owner":"MEP Consultant","confidence":96,"status":"NEEDS_REVIEW","impact":"Design change → services re-coordination → approval → site release.","why":"The MEP note directly connects the ceiling dimension to the sprinkler conflict and issuance of the MEP section.","action":"Resolve the conflict before issuing the MEP section."},
    {"id":"s5","type":"SUPPLY","severity":"MEDIUM","title":"Shade 312 is unavailable","detail":"A ready substitute (Shade 318) exists, but designer approval is required.","source_ids":"m5","owner":"Interior Designer","confidence":96,"status":"NEEDS_REVIEW","impact":"Procurement cannot lock the substitute without a design decision.","why":"Supplier reports an unavailable item and offers a live alternative pending approval.","action":"Approve or reject Shade 318."},
]

ACTION_SEED = [
    {"id":"a1","priority":"P0","title":"Resolve ceiling / sprinkler coordination","owner":"MEP Consultant","due":"Today · 16:00","status":"OPEN","reason":"Blocks MEP issuance and site release.","source_ids":"m1,m6"},
    {"id":"a2","priority":"P0","title":"Send master-bathroom visual for client sign-off","owner":"Architect","due":"Today · 17:00","status":"OPEN","reason":"Only approval exception in the current client message.","source_ids":"m4"},
    {"id":"a3","priority":"P1","title":"Approve or reject Shade 318","owner":"Interior Designer","due":"Tomorrow · 10:00","status":"OPEN","reason":"Supplier substitution is waiting on design approval.","source_ids":"m5"},
    {"id":"a4","priority":"P1","title":"Lock document-control rule to Rev 05","owner":"Project Manager","due":"Tomorrow · 09:30","status":"DONE","reason":"Prevents execution against superseded Rev 04.","source_ids":"m2,m6"},
]

PATTERNS = [
    ("APPROVAL", re.compile(r"approve|approval|approved|sign[- ]off|signoff|pending|awaiting.*approval|permission|accept|reviewed.*for approval", re.I), "Approval gate detected", "The note contains an approval or decision dependency.", "HIGH"),
    ("BLOCKER", re.compile(r"hold|holding|blocked|blocker|cannot proceed|can't proceed|stopped|paused|avoid rework|awaiting clarification|waiting for|on hold|not ready", re.I), "Execution blocker detected", "The note indicates work cannot safely or confidently proceed.", "CRITICAL"),
    ("CHANGE", re.compile(r"rev(?:ision)?\s*\d+|supersed|uploaded|updated|changed|new version|change cloud|revised|scope change|variation|design change", re.I), "Project change detected", "A revision, update, variation or changed assumption may invalidate earlier work.", "HIGH"),
    ("IMPACT", re.compile(r"conflict|clash|depends|dependency|downstream|impact|propagat|coordination|requires|before we issue|affect|affects|interfere|interface|rfi|submittal|inspection hold", re.I), "Dependency / impact detected", "The note links one event to another discipline, decision, task or milestone.", "HIGH"),
    ("SUPPLY", re.compile(r"unavailable|out of stock|substitution|alternative|shade|lead time|material|supplier|fabrication|delivery delayed|backorder|procurement", re.I), "Supply exception detected", "Availability, procurement or material status changed and may require a decision.", "MEDIUM"),
    ("ACTION", re.compile(r"need|please|confirm|clarification|issue|provide|route|review|resolve|broadcast|send|prepare|update|share|schedule|coordinate|follow up", re.I), "Next action detected", "The note contains an explicit or strongly implied next step.", "HIGH"),
]

ROLE_HINTS = {
    "architect": "Architect",
    "design": "Architect",
    "drawing": "Architect",
    "mep": "MEP Consultant",
    "mechanical": "MEP Consultant",
    "electrical": "MEP Consultant",
    "plumbing": "MEP Consultant",
    "interior": "Interior Designer",
    "finish": "Interior Designer",
    "material": "Interior Designer",
    "procurement": "Supplier",
    "supplier": "Supplier",
    "contractor": "Contractor",
    "site": "Contractor",
    "client": "Client",
    "owner": "Project Manager",
    "project manager": "Project Manager",
}

ENTITY_PATTERNS = [
    re.compile(r"\b[A-Z]{1,4}-\d{2,5}\s+(?:Rev(?:ision)?\s*)?\d+\b"),
    re.compile(r"\bRev(?:ision)?\s*\d+\b", re.I),
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:mm|cm|m|kg|kN|%)\b", re.I),
    re.compile(r"\b(?:RFI|RFP|PO|BOQ|ITP|NCR|RFQ|CO)\s*[#-]?\d*\b", re.I),
    re.compile(r"\b[A-Z]{2,6}-\d{2,5}\b"),
    re.compile(r"\b(?:Zone|Level|Floor|Room|Block|Tower)\s+[A-Z0-9-]+\b", re.I),
    re.compile(r"\b(?:shade|finish|tile|stone|marble|fixture|material)\s+[A-Za-z0-9-]+\b", re.I),
]


def extract_entities(text: str) -> list[str]:
    found: list[str] = []
    for pattern in ENTITY_PATTERNS:
        found.extend(pattern.findall(text))
    # Capture concise noun-like phrases after common construction terms.
    for match in re.findall(r"\b(?:ceiling|sprinkler|duct|beam|slab|gypsum|bathroom|kitchen|stair|façade|facade|window|door|electrical point|finish schedule|drawing|submittal|inspection)\b", text, re.I):
        found.append(match)
    output: list[str] = []
    seen = set()
    for item in found:
        value = item.strip()
        key = value.lower()
        if value and key not in seen:
            output.append(value)
            seen.add(key)
    return output[:16]


def infer_owner(text: str, signals: list[dict[str, Any]]) -> str:
    low = text.lower()
    for hint, owner in ROLE_HINTS.items():
        if hint in low:
            return owner
    types = {s["type"] for s in signals}
    if "SUPPLY" in types:
        return "Supplier"
    if "APPROVAL" in types:
        return "Project Manager"
    if "BLOCKER" in types:
        return "Project Manager"
    return "Project Manager"


def local_extract(text: str) -> dict[str, Any]:
    signal_hits: list[dict[str, Any]] = []
    for signal_type, pattern, title, reason, severity in PATTERNS:
        if pattern.search(text):
            signal_hits.append({
                "type": signal_type,
                "severity": severity,
                "title": title,
                "reason": reason,
            })
    entities = extract_entities(text)
    owner = infer_owner(text, signal_hits)
    if not signal_hits:
        intent = "CONTEXT"
        summary = "No high-signal coordination risk was detected; the note was retained as project context."
    else:
        # De-duplicate the same semantic signal if multiple patterns overlap heavily.
        unique: list[dict[str, Any]] = []
        seen = set()
        for hit in signal_hits:
            if hit["type"] not in seen:
                unique.append(hit)
                seen.add(hit["type"])
        signal_hits = unique
        intent = " · ".join(hit["type"] for hit in signal_hits)
        summary = " ".join(hit["title"] + "." for hit in signal_hits)
    confidence = min(96, 68 + len(signal_hits) * 5 + min(14, len(entities) * 2))
    return {
        "engine": "local-evidence-fallback",
        "intent": intent,
        "summary": summary,
        "entities": entities,
        "signals": signal_hits,
        "confidence": confidence,
        "owner_hint": owner,
        "provider_used": False,
    }


PROVIDER_SYSTEM_PROMPT = """You are ThreadPilot, an evidence-first construction/project coordination intelligence engine.
Given one unstructured project update, extract only facts supported by the text.
Return valid JSON only using these keys:
intent, summary, entities, signals, confidence, owner_hint, dependencies, approvals, blockers, next_actions.

signals is an array of objects with:
{type, severity, title, reason}
where type is one of CHANGE, APPROVAL, BLOCKER, IMPACT, SUPPLY, ACTION, CONTEXT and severity is CRITICAL, HIGH, MEDIUM, LOW.
entities is an array of concise project entities (drawing/revision IDs, rooms, disciplines, materials, quantities, RFI/PO numbers, etc.).
dependencies, approvals, blockers and next_actions are arrays of concise factual strings.
owner_hint must be the responsible role suggested by the evidence, or "Project Manager" if unclear.
confidence is an integer 0-100.
Never invent names, dates, dependencies, approvals, or project facts not present or strongly implied by the note.
If the note is ambiguous, lower confidence rather than inventing context."""


def _strip_json_fence(content: str) -> str:
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.I)
    content = re.sub(r"\s*```$", "", content)
    return content.strip()


def _provider_url() -> str:
    base = settings.llm_base_url.rstrip("/")
    return base if base.endswith("/chat/completions") else base + "/chat/completions"


def provider_extract(text: str) -> dict[str, Any] | None:
    if not settings.llm_api_key or not settings.llm_base_url:
        return None
    payload = {
        "model": settings.llm_model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": PROVIDER_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(_provider_url(), json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(_strip_json_fence(content))
        if not isinstance(parsed, dict):
            return None
        parsed.setdefault("intent", "CONTEXT")
        parsed.setdefault("summary", "Coordination intelligence extracted from the project update.")
        parsed.setdefault("entities", [])
        parsed.setdefault("signals", [])
        parsed.setdefault("confidence", 88)
        parsed.setdefault("owner_hint", "Project Manager")
        parsed.setdefault("dependencies", [])
        parsed.setdefault("approvals", [])
        parsed.setdefault("blockers", [])
        parsed.setdefault("next_actions", [])
        parsed["engine"] = "provider-llm-primary"
        parsed["provider_used"] = True
        return parsed
    except Exception:
        return None


def intelligence(text: str) -> dict[str, Any]:
    """Primary provider -> deterministic evidence fallback."""
    provider = provider_extract(text)
    return provider if provider is not None else local_extract(text)


def _revision_refs(text: str) -> list[tuple[str, int]]:
    pairs = re.findall(r"\b([A-Z]{1,4}-\d{2,5})\s+Rev(?:ision)?\s*(\d+)\b", text, re.I)
    if not pairs:
        # Generic revision mentions when the drawing ID is omitted.
        pairs = [("GENERIC", n) for n in re.findall(r"\bRev(?:ision)?\s*(\d+)\b", text, re.I)]
    return [(doc.upper(), int(rev)) for doc, rev in pairs]


def conflict_rows(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect generic revision/material conflicts across the current message set."""
    rows: list[dict[str, Any]] = []
    revision_mentions: dict[str, set[int]] = defaultdict(set)
    revision_sources: dict[str, list[str]] = defaultdict(list)
    superseding: list[tuple[str, int, str]] = []

    for message in messages:
        text = message["text"]
        for document_id, revision in _revision_refs(text):
            revision_mentions[document_id].add(revision)
            revision_sources[document_id].append(message["id"])
            if re.search(r"supersed|replac|current revision|latest revision|newest revision", text, re.I):
                superseding.append((document_id, revision, message["id"]))

    for document_id, revisions in revision_mentions.items():
        if len(revisions) > 1:
            ordered = sorted(revisions)
            latest = max(revisions)
            rows.append({
                "id": f"revision-{document_id}",
                "kind": "REVISION",
                "severity": "CRITICAL" if any(rev < latest for rev in revisions) else "HIGH",
                "title": f"Conflicting revisions referenced for {document_id}",
                "detail": f"Revisions {', '.join(str(x) for x in ordered)} appear in the current project memory.",
                "source_ids": ",".join(dict.fromkeys(revision_sources[document_id])),
                "recommendation": f"Confirm revision {latest} as the current execution reference and review work against older revisions.",
            })

    material_pairs = re.findall(
        r"(?:([A-Za-z][\w-]{1,30})\s+(?:is|was)\s+(?:unavailable|out of stock|delayed|cancelled)|"
        r"(?:substitut(?:e|ion)|alternative)\s+(?:from|for)?\s*([A-Za-z0-9 -]{2,30}))",
        " ".join(m["text"] for m in messages), re.I,
    )
    if material_pairs:
        rows.append({
            "id": "material-exception",
            "kind": "SUPPLY",
            "severity": "HIGH",
            "title": "Material availability exception needs a decision",
            "detail": "The current message stream contains an unavailable/delayed material or substitution path.",
            "source_ids": ",".join(m["id"] for m in messages if re.search(r"unavailable|out of stock|delayed|cancelled|substitut|alternative", m["text"], re.I)),
            "recommendation": "Assign the design/procurement owner, capture the approved alternative and update the execution reference.",
        })
    return rows


def build_impact(signal: dict[str, Any], messages: list[dict[str, Any]]) -> dict[str, Any]:
    source_ids = {x.strip() for x in signal.get("source_ids", "").split(",") if x.strip()}
    sources = [m for m in messages if m["id"] in source_ids]
    affected = signal.get("owner") or "Coordination owner"
    stages = [
        {"step": 1, "label": "Evidence", "value": signal.get("title", "Project signal"), "state": "ACTIVE"},
        {"step": 2, "label": "Affected", "value": affected, "state": "AT RISK" if signal.get("severity") in ("CRITICAL", "HIGH") else "ACTIVE"},
        {"step": 3, "label": "Dependency", "value": signal.get("impact") or "Review downstream work", "state": "ACTIVE"},
        {"step": 4, "label": "Approval / gate", "value": "Explicit human review" if signal.get("type") == "APPROVAL" else "Check required approvals", "state": "AT RISK" if signal.get("type") == "APPROVAL" else "PENDING"},
        {"step": 5, "label": "Next action", "value": signal.get("action") or "Create owner action", "state": "ACTION"},
    ]
    return {"signal": signal, "sources": sources, "stages": stages}


def build_graph(signals: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a graph from live signals rather than relying on a fixed scenario graph."""
    nodes: list[dict[str, Any]] = []
    edges: list[list[str]] = []
    node_key: dict[str, str] = {}

    def add_node(label: str, kind: str) -> str:
        key = f"n{len(nodes)+1}"
        normalized = label.strip().lower()
        if normalized in node_key:
            return node_key[normalized]
        nodes.append({"id": key, "label": label.strip()[:80], "kind": kind})
        node_key[normalized] = key
        return key

    for signal in signals:
        root = add_node(signal["title"], signal["type"])
        owner = add_node(signal.get("owner", "Coordination owner"), "OWNER")
        action = add_node(signal.get("action", "Review and act"), "ACTION")
        edges.extend([[root, owner], [root, action]])
        if signal.get("type") in {"CHANGE", "IMPACT"}:
            dep = add_node(signal.get("impact", "Downstream dependency"), "DEPENDENCY")
            edges.append([root, dep])
        if signal.get("type") == "APPROVAL":
            gate = add_node("Approval gate", "GATE")
            edges.append([root, gate])
            edges.append([gate, action])

    # One compact causal spine for readability; relationships remain data-derived.
    return {"nodes": nodes[:40], "edges": edges[:80]}
