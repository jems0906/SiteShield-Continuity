from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, Handoff
from app.security.roles import Role, current_role

router = APIRouter(prefix="/handoffs", tags=["handoffs"])


@router.get("")
def list_handoffs(db: Session = Depends(get_db), role: Role = Depends(current_role)):
    return db.scalars(select(Handoff).order_by(Handoff.id)).all()


@router.post("/{handoff_id}/acknowledge")
def acknowledge(handoff_id: str, db: Session = Depends(get_db), role: Role = Depends(current_role)):
    if role not in {Role.analyst, Role.reviewer}:
        raise HTTPException(status_code=403, detail="Only analyst or reviewer may acknowledge a handoff")
    handoff = db.get(Handoff, handoff_id)
    if not handoff:
        raise HTTPException(status_code=404, detail="Handoff not found")
    handoff.acknowledged_by = role.value
    db.add(AuditLog(actor_role=role.value, action="handoff_acknowledged", record_type="handoff", record_id=handoff_id))
    db.commit()
    return handoff