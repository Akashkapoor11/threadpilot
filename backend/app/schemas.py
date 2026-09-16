from typing import Any

from pydantic import BaseModel, Field, field_validator


class CaptureRequest(BaseModel):
    text: str = Field(min_length=3, max_length=5000)
    channel: str = Field(default="Captured note", min_length=2, max_length=50)
    sender: str = Field(default="You", min_length=1, max_length=120)


class IntelligenceSignal(BaseModel):
    type: str
    severity: str
    title: str
    reason: str = ""


class IntelligenceResult(BaseModel):
    engine: str
    intent: str
    summary: str
    entities: list[str]
    signals: list[IntelligenceSignal]
    confidence: int
    owner_hint: str = "Project Manager"
    dependencies: list[str] = Field(default_factory=list)
    approvals: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    provider_used: bool = False

    @field_validator("confidence")
    @classmethod
    def confidence_bounds(cls, value: int) -> int:
        return max(0, min(100, value))


class StakeholderUpdate(BaseModel):
    role: str = Field(min_length=2, max_length=120)
    focus: str = Field(min_length=2, max_length=240)
    status: str = Field(default="ACTIVE", min_length=4, max_length=30)


class AlertRequest(BaseModel):
    channel: str = Field(default="In-app", min_length=2, max_length=40)
    recipient: str = Field(min_length=2, max_length=160)


class HealthResponse(BaseModel):
    ok: bool
    service: str
    version: str
    database: str
    engine: str
    provider_configured: bool


class ProjectResponse(BaseModel):
    project: dict[str, Any]
    people: list[dict[str, Any]]
    messages: list[dict[str, Any]]
    signals: list[dict[str, Any]]
    actions: list[dict[str, Any]]
    alerts: list[dict[str, Any]]
    audit: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    graph: dict[str, Any]
    metrics: dict[str, Any]
    brief: dict[str, Any]
