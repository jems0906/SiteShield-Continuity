from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, WorkOrder
from app.schemas import Acceptance, WorkCompletion
from app.security.roles import Role, current_role
from app.services.work_order_workflow import accept_work_order

router = APIRouter(prefix="/work-orders", tags=["work orders"])


def visible(order: WorkOrder, role: Role) -> bool:
    return role != Role.vendor or order.vendor_visible


@router.get("")
def list_work_orders(db: Session = Depends(get_db), role: Role = Depends(current_role)):
    return [order for order in db.scalars(select(WorkOrder).order_by(WorkOrder.id)).all() if visible(order, role)]


@router.post("/{order_id}/acknowledge")
def acknowledge(order_id: str, db: Session = Depends(get_db), role: Role = Depends(current_role)):
    if role != Role.vendor:
        raise HTTPException(status_code=403, detail="Vendor role required")
    order = db.get(WorkOrder, order_id)
    if not order or not visible(order, role):
        raise HTTPException(status_code=404, detail="Work order not found")
    if order.status != "scheduled":
        raise HTTPException(status_code=409, detail="Only scheduled work can be acknowledged")
    order.vendor_acknowledgment = "Acknowledged in demo workspace"
    order.status = "in_progress"
    db.add(AuditLog(actor_role=role.value, action="vendor_acknowledged", record_type="work_order", record_id=order_id))
    db.commit()
    return order


@router.post("/{order_id}/accept")
def accept(order_id: str, acceptance: Acceptance, db: Session = Depends(get_db), role: Role = Depends(current_role)):
    if role != Role.reviewer:
        raise HTTPException(status_code=403, detail="Reviewer role required")
    order = db.get(WorkOrder, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Work order not found")
    accept_work_order(db, order, role.value, acceptance.model_dump())
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/complete")
def complete(order_id: str, payload: WorkCompletion, db: Session = Depends(get_db), role: Role = Depends(current_role)):
    if role != Role.vendor:
        raise HTTPException(status_code=403, detail="Vendor role required")
    order = db.get(WorkOrder, order_id)
    if not order or not visible(order, role):
        raise HTTPException(status_code=404, detail="Work order not found")
    if order.status != "in_progress":
        raise HTTPException(status_code=409, detail="Only acknowledged work can be completed")
    order.completion_record = payload.completion_record
    order.diagnostic = {**order.diagnostic, "vendor_assessment": payload.vendor_assessment, "repair_evidence_reference": payload.repair_evidence_reference}
    order.status = "completed"
    db.add(AuditLog(actor_role=role.value, action="vendor_completed", record_type="work_order", record_id=order_id))
    db.commit()
    db.refresh(order)
    return order