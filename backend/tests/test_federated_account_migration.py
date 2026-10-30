from hashlib import sha256
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Account, AuditLog


def test_federated_migration_pseudonymizes_subject_and_audit_reference(tmp_path, monkeypatch):
    database_path = tmp_path / "federated-migration.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.upgrade(config, "0005_account_allowed_roles")

    old_username = "entra:123e4567-e89b-12d3-a456-426614174000:123e4567-e89b-12d3-a456-426614174001"
    with Session(create_engine(database_url)) as db:
        db.add(Account(
            username=old_username,
            display_name="Synthetic Subject",
            password_hash=None,
            role="reviewer",
            roles=["analyst", "reviewer"],
        ))
        db.add(AuditLog(actor_role="reviewer", action="entra_login", record_type="account", record_id=old_username))
        db.commit()

    command.upgrade(config, "head")
    anonymized_username = f"entra:{sha256(old_username.encode()).hexdigest()}"
    with Session(create_engine(database_url)) as db:
        account = db.get(Account, anonymized_username)
        audit_reference = db.scalar(select(AuditLog.record_id).where(AuditLog.record_type == "account"))

    assert account is not None
    assert account.display_name == "Workspace member"
    assert account.role == "reviewer"
    assert account.roles == ["analyst", "reviewer"]
    assert audit_reference == anonymized_username