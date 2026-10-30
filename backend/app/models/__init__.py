from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    category: Mapped[str] = mapped_column(String(40))
    owner: Mapped[str] = mapped_column(String(100))
    inspection_date: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(40))
    site: Mapped[str] = mapped_column(String(80))
    availability: Mapped[float] = mapped_column(default=1.0)
    monitored_days: Mapped[int] = mapped_column(Integer, default=30)


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    asset_id: Mapped[str] = mapped_column(String(40))
    checklist_item: Mapped[str] = mapped_column(String(160))
    result: Mapped[str] = mapped_column(String(30))
    evidence_reference: Mapped[str] = mapped_column(String(160))
    priority: Mapped[str] = mapped_column(String(30))
    owner: Mapped[str] = mapped_column(String(100))
    corrective_action: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40))


class AlarmEvent(Base):
    __tablename__ = "alarm_events"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    source_record_id: Mapped[str] = mapped_column(String(80), index=True)
    asset_id: Mapped[str] = mapped_column(String(40), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    classification: Mapped[str] = mapped_column(String(40))
    summary: Mapped[str] = mapped_column(String(240))
    duplicate_of: Mapped[str | None] = mapped_column(String(40), nullable=True)
    raw_event: Mapped[dict] = mapped_column(JSON, default=dict)


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    asset_id: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(160))
    scope: Mapped[str] = mapped_column(Text)
    accountable_owner: Mapped[str] = mapped_column(String(100))
    scheduled_window: Mapped[str] = mapped_column(String(120))
    vendor_acknowledgment: Mapped[str] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(40))
    completion_record: Mapped[str] = mapped_column(Text, default="")
    acceptance_criteria: Mapped[list] = mapped_column(JSON, default=list)
    reviewer_acceptance: Mapped[str] = mapped_column(String(40), default="pending")
    vendor_visible: Mapped[bool] = mapped_column(Boolean, default=False)
    diagnostic: Mapped[dict] = mapped_column(JSON, default=dict)
    functional_retest: Mapped[dict] = mapped_column(JSON, default=dict)
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Handoff(Base):
    __tablename__ = "handoffs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    shift: Mapped[str] = mapped_column(String(100))
    open_incidents: Mapped[list] = mapped_column(JSON, default=list)
    unresolved_defects: Mapped[list] = mapped_column(JSON, default=list)
    work_in_progress: Mapped[list] = mapped_column(JSON, default=list)
    temporary_arrangements: Mapped[list] = mapped_column(JSON, default=list)
    next_owner: Mapped[str] = mapped_column(String(100))
    acknowledged_by: Mapped[str] = mapped_column(String(100), default="")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    scenario_type: Mapped[str] = mapped_column(String(80))
    timeline: Mapped[list] = mapped_column(JSON, default=list)
    decisions: Mapped[list] = mapped_column(JSON, default=list)
    communications: Mapped[list] = mapped_column(JSON, default=list)
    findings: Mapped[list] = mapped_column(JSON, default=list)
    improvements: Mapped[list] = mapped_column(JSON, default=list)
    business_impact: Mapped[dict] = mapped_column(JSON, default=dict)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_role: Mapped[str] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(120))
    record_type: Mapped[str] = mapped_column(String(40))
    record_id: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class Account(Base):
    __tablename__ = "accounts"

    username: Mapped[str] = mapped_column(String(80), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)