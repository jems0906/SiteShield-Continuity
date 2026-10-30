from sqlalchemy.orm import Session

from app.models import AuditLog, Exercise


def record_exercise_action(session: Session, exercise: Exercise, role: str, action: dict) -> Exercise:
    exercise.decisions = [*exercise.decisions, action]
    session.add(AuditLog(actor_role=role, action="exercise_decision_recorded", record_type="exercise", record_id=exercise.id))
    return exercise