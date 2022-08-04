"""Create user table

Revision ID: 771c311adcf1
Revises:
Create Date: 2022-08-03 16:55:39.021710

"""
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "771c311adcf1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("password", sa.Text(), nullable=False),
    )


def downgrade():
    op.drop_table("user")
