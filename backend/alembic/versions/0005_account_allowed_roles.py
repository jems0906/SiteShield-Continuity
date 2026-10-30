"""Store Entra roles allowed for the account separately from active role."""
from alembic import op
import sqlalchemy as sa

revision = "0005_account_allowed_roles"
down_revision = "0004_federated_accounts"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("accounts", sa.Column("roles", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("accounts", "roles")