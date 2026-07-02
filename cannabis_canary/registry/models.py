"""SQLAlchemy models for the registry (PHI store) and audit log."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class CannabisHistoryRecord(Base):
    """One captured Cannabis Use social history (a QuestionnaireResponse)."""

    __tablename__ = "cannabis_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    patient_id: Mapped[str] = mapped_column(String(128), index=True)
    author_id: Mapped[str] = mapped_column(String(128))
    authored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    exposure_status: Mapped[str] = mapped_column(String(32))
    thc_mg_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)
    response_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AuditEvent(Base):
    """Minimum-necessary audit trail: who did what to whose record, when."""

    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    actor: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(32))  # view | capture | login
    patient_id: Mapped[str] = mapped_column(String(128), index=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
