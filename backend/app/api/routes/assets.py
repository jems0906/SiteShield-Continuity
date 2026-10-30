from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Asset
from app.security.roles import Role, current_role

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("")
def list_assets(db: Session = Depends(get_db), role: Role = Depends(current_role)):
    return db.scalars(select(Asset).order_by(Asset.id)).all()