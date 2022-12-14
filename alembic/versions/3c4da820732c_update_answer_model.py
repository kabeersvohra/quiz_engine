"""Update answer model

Revision ID: 3c4da820732c
Revises: 00a773b93f29
Create Date: 2022-08-04 15:08:34.895834

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "3c4da820732c"
down_revision = "00a773b93f29"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("question_correct_answers")
    op.add_column("answer", sa.Column("correct", sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("answer", "correct")
    op.create_table(
        "question_correct_answers",
        sa.Column("id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "question_id", postgresql.UUID(), autoincrement=False, nullable=False
        ),
        sa.Column("answer_id", postgresql.UUID(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["answer_id"], ["answer.id"], name="question_correct_answers_answer_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["question.id"],
            name="question_correct_answers_question_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="question_correct_answers_pkey"),
        sa.UniqueConstraint(
            "question_id",
            "answer_id",
            name="question_correct_answers_question_id_answer_id_key",
        ),
    )
    # ### end Alembic commands ###
