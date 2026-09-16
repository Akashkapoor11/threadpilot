from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def utcnow():
    return datetime.now(timezone.utc)

class Stakeholder(Base):
    __tablename__ = "stakeholders"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    focus: Mapped[str] = mapped_column(String(240), nullable=False)
    initials: Mapped[str] = mapped_column(String(8), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    sender: Mapped[str] = mapped_column(String(120), nullable=False)
    time_label: Mapped[str] = mapped_column(String(30), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Signal(Base):
    __tablename__ = "signals"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    source_ids: Mapped[str] = mapped_column(String(500), nullable=False)
    owner: Mapped[str] = mapped_column(String(200), nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, default=80)
    status: Mapped[str] = mapped_column(String(30), default="NEEDS_REVIEW")
    impact: Mapped[str] = mapped_column(Text, nullable=False)
    why: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Action(Base):
    __tablename__ = "actions"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    owner: Mapped[str] = mapped_column(String(160), nullable=False)
    due: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    source_ids: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    signal_id: Mapped[str] = mapped_column(String(40), nullable=False)
    recipient: Mapped[str] = mapped_column(String(160), nullable=False)
    channel: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="QUEUED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Audit(Base):
    __tablename__ = "audit"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    event: Mapped[str] = mapped_column(String(80), nullable=False)
    entity: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(80), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ProjectMeta(Base):
    __tablename__ = "project_meta"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    demo_mode: Mapped[bool] = mapped_column(Boolean, default=True)
