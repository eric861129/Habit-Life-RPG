"""Create the complete book MVP schema."""

from alembic import op
import sqlalchemy as sa


revision = "0001_complete_mvp_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.Unicode(length=32), nullable=False),
        sa.Column("username_normalized", sa.Unicode(length=32), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("exp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("level >= 1", name="ck_users_level_positive"),
        sa.CheckConstraint("exp >= 0", name="ck_users_exp_nonnegative"),
        sa.CheckConstraint("gold >= 0", name="ck_users_gold_nonnegative"),
        sa.UniqueConstraint("username_normalized"),
    )
    op.create_index("ix_users_username_normalized", "users", ["username_normalized"])

    op.create_table(
        "habits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.Unicode(length=120), nullable=False),
        sa.Column("description", sa.Unicode(length=500), nullable=True),
        sa.Column("category", sa.Unicode(length=40), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("streak_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_checkin_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("streak_count >= 0", name="ck_habits_streak_nonnegative"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_habits_user_active", "habits", ["user_id", "is_archived"])

    op.create_table(
        "habit_checkins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("habit_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("checkin_date", sa.Date(), nullable=False),
        sa.Column("checked_in_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exp_earned", sa.Integer(), nullable=False),
        sa.Column("gold_earned", sa.Integer(), nullable=False),
        sa.CheckConstraint("exp_earned >= 0", name="ck_checkins_exp_nonnegative"),
        sa.CheckConstraint("gold_earned >= 0", name="ck_checkins_gold_nonnegative"),
        sa.ForeignKeyConstraint(["habit_id"], ["habits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("habit_id", "checkin_date", name="uq_habit_checkin_day"),
    )
    op.create_index(
        "ix_habit_checkins_user_date",
        "habit_checkins",
        ["user_id", "checkin_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_habit_checkins_user_date", table_name="habit_checkins")
    op.drop_table("habit_checkins")
    op.drop_index("ix_habits_user_active", table_name="habits")
    op.drop_table("habits")
    op.drop_index("ix_users_username_normalized", table_name="users")
    op.drop_table("users")
