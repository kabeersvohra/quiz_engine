"""Allow multiple answers

Revision ID: f050aac5b4c5
Revises: f2393537f216
Create Date: 2022-08-04 13:35:49.153767

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "f050aac5b4c5"
down_revision = "f2393537f216"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "question_correct_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("answer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["answer_id"],
            ["answer.id"],
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["question.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", "answer_id"),
    )
    op.drop_constraint("question_correct_answer_fkey", "question", type_="foreignkey")
    op.drop_column("question", "correct_answer")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "question",
        sa.Column(
            "correct_answer", postgresql.UUID(), autoincrement=False, nullable=True
        ),
    )
    op.create_foreign_key(
        "question_correct_answer_fkey", "question", "answer", ["correct_answer"], ["id"]
    )
    op.drop_table("question_correct_answers")
    # ### end Alembic commands ###
