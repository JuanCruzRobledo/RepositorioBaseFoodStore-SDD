"""initial empty migration (placeholder, models live in us-001-auth and beyond)

Revision ID: 0001
Revises:
Create Date: 2026-05-10

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
    )


def downgrade() -> None:
    op.drop_table("roles")
