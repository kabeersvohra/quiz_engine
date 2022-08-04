"""Add published to quiz

Revision ID: a3fe450d0d7d
Revises: 3c4da820732c
Create Date: 2022-08-04 15:24:00.294827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3fe450d0d7d'
down_revision = '3c4da820732c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quiz', sa.Column('published', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('quiz', 'published')
    # ### end Alembic commands ###
