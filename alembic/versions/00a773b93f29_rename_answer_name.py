"""Rename answer name

Revision ID: 00a773b93f29
Revises: e89288485c17
Create Date: 2022-08-04 13:43:18.131412

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00a773b93f29'
down_revision = 'e89288485c17'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('answer', sa.Column('answer', sa.Text(), nullable=False))
    op.drop_column('answer', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('answer', sa.Column('name', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_column('answer', 'answer')
    # ### end Alembic commands ###