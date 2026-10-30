from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditFinding
from app.security.roles import Role, current_role

router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("")
def list_findings(db: Session = Depends(get_db), role: Role = Depends(current_role)):
    return db.scalars(select(AuditFinding).order_by(AuditFinding.id)).all()