from sqlalchemy import delete

from app.config import settings
from app.database import SessionLocal
from app.models import AlarmEvent, AuditFinding, AuditLog, Asset, Exercise, Handoff, WorkOrder
from scripts.seed_demo import seed


def reset_demo() -> None:
    if not settings.demo_mode or not settings.allow_demo_reset:
        raise RuntimeError("Demo reset requires DEMO_MODE=true and ALLOW_DEMO_RESET=true.")

    with SessionLocal() as db:
        for model in (AuditLog, Exercise, Handoff, WorkOrder, AlarmEvent, AuditFinding, Asset):
            db.execute(delete(model))
        db.commit()

    seed()


if __name__ == "__main__":
    reset_demo()