import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_threadpilot.db")

from fastapi.testclient import TestClient

from app.engine import conflict_rows, intelligence
from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["ok"] is True
        assert "provider-first" in response.json()["engine"]


def test_project_has_as01_scenario():
    with TestClient(app) as client:
        data = client.get("/api/project").json()
        assert len(data["people"]) >= 6
        assert len(data["messages"]) >= 6
        assert len(data["signals"]) >= 5
        assert len(data["actions"]) >= 4
        assert data["project"]["code"] == "RS-24"


def test_generic_local_intelligence_handles_unseen_construction_note():
    result = intelligence(
        "RFI-214 confirms the electrical containment must move above the beam. "
        "The contractor is waiting for the revised soffit drawing before closing the ceiling."
    )
    types = {signal["type"] for signal in result["signals"]}
    assert {"IMPACT", "BLOCKER", "CHANGE", "ACTION"}.intersection(types)
    assert any("RFI-214".lower() in entity.lower() for entity in result["entities"])


def test_generic_revision_conflict_detection():
    messages = [
        {"id": "x1", "text": "Please build from D-101 Rev 2."},
        {"id": "x2", "text": "D-101 Rev 4 is uploaded and supersedes Rev 2."},
    ]
    rows = conflict_rows(messages)
    assert any(row["kind"] == "REVISION" for row in rows)


def test_live_capture_creates_signal_action_and_alert():
    with TestClient(app) as client:
        response = client.post(
            "/api/messages",
            json={
                "text": "Rev 06 uploaded. Please confirm the MEP section before site release; sprinkler route is changed.",
                "channel": "Meeting",
                "sender": "Project Manager",
            },
        )
        assert response.status_code == 200
        data = response.json()["project"]
        assert any(item["id"] == response.json()["message_id"] for item in data["messages"])
        assert any(action["status"] == "OPEN" for action in data["actions"])
        message_id = response.json()["message_id"]
        signal = next(item for item in data["signals"] if item["source_ids"].startswith(message_id))
        routed = client.post(
            f"/api/signals/{signal['id']}/route",
            json={"recipient": "MEP Consultant", "channel": "In-app"},
        )
        assert routed.status_code == 200
        assert routed.json()["metrics"]["alerts"] >= 1


def test_stakeholder_management():
    with TestClient(app) as client:
        response = client.put(
            "/api/stakeholders/p2",
            json={
                "role": "Lead Services Consultant",
                "focus": "HVAC, sprinkler and issue coordination",
                "status": "ACTIVE",
            },
        )
        assert response.status_code == 200
        person = next(p for p in response.json()["people"] if p["id"] == "p2")
        assert person["role"] == "Lead Services Consultant"
