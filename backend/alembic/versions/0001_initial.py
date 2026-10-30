"""Create the SiteShield demo schema."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "assets",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("owner", sa.String(100), nullable=False),
        sa.Column("inspection_date", sa.String(20), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("site", sa.String(80), nullable=False),
        sa.Column("availability", sa.Float(), nullable=False),
        sa.Column("monitored_days", sa.Integer(), nullable=False),
    )
    op.create_table(
        "audit_findings",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("asset_id", sa.String(40), nullable=False),
        sa.Column("checklist_item", sa.String(160), nullable=False),
        sa.Column("result", sa.String(30), nullable=False),
        sa.Column("evidence_reference", sa.String(160), nullable=False),
        sa.Column("priority", sa.String(30), nullable=False),
        sa.Column("owner", sa.String(100), nullable=False),
        sa.Column("corrective_action", sa.Text(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
    )
    op.create_table(
        "alarm_events",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("source_record_id", sa.String(80), nullable=False),
        sa.Column("asset_id", sa.String(40), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("classification", sa.String(40), nullable=False),
        sa.Column("summary", sa.String(240), nullable=False),
        sa.Column("duplicate_of", sa.String(40), nullable=True),
        sa.Column("raw_event", sa.JSON(), nullable=False),
    )
    op.create_index("ix_alarm_events_source_record_id", "alarm_events", ["source_record_id"])
    op.create_index("ix_alarm_events_asset_id", "alarm_events", ["asset_id"])
    op.create_index("ix_alarm_events_occurred_at", "alarm_events", ["occurred_at"])
    op.create_table(
        "work_orders",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("asset_id", sa.String(40), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("accountable_owner", sa.String(100), nullable=False),
        sa.Column("scheduled_window", sa.String(120), nullable=False),
        sa.Column("vendor_acknowledgment", sa.String(240), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("completion_record", sa.Text(), nullable=False),
        sa.Column("acceptance_criteria", sa.JSON(), nullable=False),
        sa.Column("reviewer_acceptance", sa.String(40), nullable=False),
        sa.Column("vendor_visible", sa.Boolean(), nullable=False),
        sa.Column("diagnostic", sa.JSON(), nullable=False),
        sa.Column("functional_retest", sa.JSON(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "handoffs",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("shift", sa.String(100), nullable=False),
        sa.Column("open_incidents", sa.JSON(), nullable=False),
        sa.Column("unresolved_defects", sa.JSON(), nullable=False),
        sa.Column("work_in_progress", sa.JSON(), nullable=False),
        sa.Column("temporary_arrangements", sa.JSON(), nullable=False),
        sa.Column("next_owner", sa.String(100), nullable=False),
        sa.Column("acknowledged_by", sa.String(100), nullable=False),
    )
    op.create_table(
        "exercises",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("scenario_type", sa.String(80), nullable=False),
        sa.Column("timeline", sa.JSON(), nullable=False),
        sa.Column("decisions", sa.JSON(), nullable=False),
        sa.Column("communications", sa.JSON(), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False),
        sa.Column("improvements", sa.JSON(), nullable=False),
        sa.Column("business_impact", sa.JSON(), nullable=False),
    )
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("actor_role", sa.String(40), nullable=False),
        sa.Column("action", sa.String(120), nullable=False),
        sa.Column("record_type", sa.String(40), nullable=False),
        sa.Column("record_id", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("audit_log")
    op.drop_table("exercises")
    op.drop_table("handoffs")
    op.drop_table("work_orders")
    op.drop_index("ix_alarm_events_occurred_at", table_name="alarm_events")
    op.drop_index("ix_alarm_events_asset_id", table_name="alarm_events")
    op.drop_index("ix_alarm_events_source_record_id", table_name="alarm_events")
    op.drop_table("alarm_events")
    op.drop_table("audit_findings")
    op.drop_table("assets")