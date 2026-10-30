"""Pseudonymize stored Entra subjects and display names."""
from hashlib import sha256

from alembic import op
import sqlalchemy as sa

revision = "0006_pseudonymize_fed"
down_revision = "0005_account_allowed_roles"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    accounts = sa.table(
        "accounts",
        sa.column("username", sa.String(80)),
        sa.column("display_name", sa.String(160)),
    )
    audit_log = sa.table(
        "audit_log",
        sa.column("record_type", sa.String(40)),
        sa.column("record_id", sa.String(80)),
    )
    subjects = connection.execute(
        sa.select(accounts.c.username).where(accounts.c.username.like("entra:%"))
    ).scalars().all()
    for old_username in subjects:
        new_username = f"entra:{sha256(old_username.encode()).hexdigest()}"
        connection.execute(
            sa.update(accounts)
            .where(accounts.c.username == old_username)
            .values(username=new_username, display_name="Workspace member")
        )
        connection.execute(
            sa.update(audit_log)
            .where(sa.and_(audit_log.c.record_type == "account", audit_log.c.record_id == old_username))
            .values(record_id=new_username)
        )


def downgrade():
    raise NotImplementedError("Federated account identifiers are pseudonymized irreversibly.")