from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlarmEvent, AuditLog
from app.schemas import AlarmImport
from app.security.roles import Role, current_role
from app.services.alarm_metrics import CLASSIFICATIONS, build_metrics, reconcile_event

router = APIRouter(prefix="/alarms", tags=["alarms"])


@router.get("")
def list_events(db: Session = Depends(get_db), role: Role = Depends(current_role)):
    return db.scalars(select(AlarmEvent).order_by(AlarmEvent.occurred_at.desc())).all()


@router.get("/metrics")
def metrics(window_days: int = Query(default=30, ge=1, le=365), db: Session = Depends(get_db), role: Role = Depends(current_role)):
    result = build_metrics(db, window_days)
    result["demonstration"] = True
    result["notice"] = "Synthetic fixture data; not evidence of achieved alarm reduction or security performance."
    return result


@router.post("/import", status_code=201)
def import_event(payload: AlarmImport, db: Session = Depends(get_db), role: Role = Depends(current_role)):
    if role not in {Role.analyst, Role.reviewer}:
        raise HTTPException(status_code=403, detail="Only analyst or reviewer may import synthetic events")
    if payload.classification not in CLASSIFICATIONS - {"duplicate"}:
        raise HTTPException(status_code=422, detail="Invalid event classification")
    event = reconcile_event(db, payload.model_dump())
    if event not in db:
        db.add(event)
    db.add(AuditLog(actor_role=role.value, action="alarm_event_imported", record_type="alarm_event", record_id=event.id))
    db.commit()
    db.refresh(event)
    return event