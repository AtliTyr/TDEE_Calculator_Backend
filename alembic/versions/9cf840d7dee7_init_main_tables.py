"""init main tables

Revision ID: 9cf840d7dee7
Revises: a10e3fc90f59
Create Date: 2026-01-02 20:22:05.176958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = '9cf840d7dee7'
down_revision: Union[str, Sequence[str], None] = 'a10e3fc90f59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Типы активности
    op.create_table(
        "activity_levels",
        sa.Column("id", sa.SmallInteger(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("factor", sa.Numeric(3, 2), nullable=False),
    )

    # Цели
    op.create_table(
        "goals",
        sa.Column("id", sa.SmallInteger(), primary_key=True),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
    )

    # Пользовательская информация
    op.create_table(
        "user_profiles",
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("name", sa.String()),
        sa.Column("gender", sa.String(length=6), nullable=False),
        sa.Column("birth_date", sa.Date()),
        sa.Column("height_cm", sa.Integer()),
        sa.Column("weight_kg", sa.Integer()),
        sa.Column(
            "activity_level_id",
            sa.SmallInteger(),
            sa.ForeignKey("activity_levels.id"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_check_constraint(
        "ck_user_profiles_gender",
        "user_profiles",
        "gender IN ('male', 'female')",
    )

    # Вычисления
    op.create_table(
        "calculations",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "goal_id",
            sa.SmallInteger(),
            sa.ForeignKey("goals.id"),
            nullable=False,
        ),
        # sa.Column("formula_used", sa.String(), nullable=False),
        sa.Column("input_data", JSONB, nullable=False),
        sa.Column("results", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Seed reference data
    op.bulk_insert(
        sa.table(
            "activity_levels",
            sa.column("id", sa.SmallInteger),
            sa.column("code", sa.String),
            sa.column("name", sa.String),
            sa.column("factor", sa.Numeric),
        ),
        [
            {"id": 1, "code": "sedentary", "name": "Сидячая", "factor": 1.20},
            {"id": 2, "code": "light", "name": "Лёгкая", "factor": 1.375},
            {"id": 3, "code": "moderate", "name": "Умеренная", "factor": 1.55},
            {"id": 4, "code": "high", "name": "Высокая", "factor": 1.725},
            {"id": 5, "code": "extreme", "name": "Экстремальная", "factor": 1.90},
        ],
    )

    op.bulk_insert(
        sa.table(
            "goals",
            sa.column("id", sa.SmallInteger),
            sa.column("code", sa.String),
            sa.column("name", sa.String),
        ),
        [
            {"id": 1, "code": "cut", "name": "Похудеть"},
            {"id": 2, "code": "maintain", "name": "Поддерживать"},
            {"id": 3, "code": "bulk", "name": "Набрать"},
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("calculations")

    op.drop_constraint(
        "ck_user_profiles_gender",
        "user_profiles",
        type_="check",
    )
    op.drop_table("user_profiles")

    op.drop_table("goals")
    op.drop_table("activity_levels")
    op.drop_table("users")


    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
