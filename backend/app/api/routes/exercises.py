from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Exercise
from app.schemas import Decision
from app.security.roles import Role, current_role
from app.services.exercise_actions import record_exercise_action

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("")
def list_exercises(db: Session = Depends(get_db), role: Role = Depends(current_role)):
    return db.scalars(select(Exercise).order_by(Exercise.id)).all()


@router.post("/{exercise_id}/decisions")
def add_decision(exercise_id: str, payload: Decision, db: Session = Depends(get_db), role: Role = Depends(current_role)):
    if role not in {Role.analyst, Role.reviewer}:
        raise HTTPException(status_code=403, detail="Only analyst or reviewer may record exercise decisions")
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    record_exercise_action(db, exercise, role.value, payload.model_dump())
    db.commit()
    db.refresh(exercise)
    return exercise