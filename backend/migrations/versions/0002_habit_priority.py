"""Add Habit priority for the document-driven change example."""

from alembic import op
import sqlalchemy as sa


revision = "0002_habit_priority"
down_revision = "0001_complete_mvp_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("habits") as batch_op:
        batch_op.add_column(
            sa.Column(
                "priority",
                sa.String(length=10),
                nullable=False,
                server_default="medium",
            )
        )
        batch_op.create_check_constraint(
            "ck_habits_priority_allowed",
            "priority IN ('high', 'medium', 'low')",
        )


def downgrade() -> None:
    with op.batch_alter_table("habits") as batch_op:
        batch_op.drop_constraint("ck_habits_priority_allowed", type_="check")
        batch_op.drop_column("priority")
