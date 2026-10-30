from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import AuditLog, WorkOrder


def accept_work_order(session: Session, order: WorkOrder, role: str, acceptance: dict) -> WorkOrder:
    if order.status != "completed":
        raise HTTPException(status_code=409, detail="Work must be completed before reviewer acceptance")
    if acceptance.get("functional_retest") is not True:
        raise HTTPException(status_code=422, detail="A successful functional retest is required")
    if acceptance.get("coverage_reviewed") is not True:
        raise HTTPException(status_code=422, detail="Monitoring coverage review is required")
    order.reviewer_acceptance = "accepted"
    order.functional_retest = {
        "passed": True,
        "coverage_reviewed": True,
        "notes": acceptance.get("notes", ""),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    order.status = "accepted"
    order.updated_at = datetime.now(timezone.utc)
    session.add(AuditLog(actor_role=role, action="accepted", record_type="work_order", record_id=order.id))
    return order