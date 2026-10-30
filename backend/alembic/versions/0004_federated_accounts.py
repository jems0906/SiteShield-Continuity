"""Allow federated accounts without local password hashes."""
from alembic import op
import sqlalchemy as sa

revision = "0004_federated_accounts"
down_revision = "0003_account_display_name"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.alter_column("password_hash", existing_type=sa.String(255), nullable=True)


def downgrade():
    with op.batch_alter_table("accounts") as batch_op:
        batch_op.alter_column("password_hash", existing_type=sa.String(255), nullable=False)