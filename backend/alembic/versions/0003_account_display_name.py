"""Add account display names for federated identities."""
from alembic import op
import sqlalchemy as sa

revision = "0003_account_display_name"
down_revision = "0002_accounts"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("accounts", sa.Column("display_name", sa.String(160), nullable=True))


def downgrade():
    op.drop_column("accounts", "display_name")