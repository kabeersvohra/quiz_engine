import uuid

from sqlalchemy import Boolean, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)


class QuizQuestions(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = (UniqueConstraint("quiz_id", "question_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(ForeignKey("quiz.id"), nullable=False)
    question_id = Column(ForeignKey("question.id"), nullable=False)


class QuestionAnswers(Base):
    __tablename__ = "question_answers"
    __table_args__ = (UniqueConstraint("question_id", "answer_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(ForeignKey("question.id"), nullable=False)
    answer_id = Column(ForeignKey("answer.id"), nullable=False)


class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    name = Column(Text, nullable=False)
    questions = relationship("Question", secondary="quiz_questions")
    published = Column(Boolean, default=False)


class Question(Base):
    __tablename__ = "question"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    answers = relationship("Answer", secondary="question_answers")


class Answer(Base):
    __tablename__ = "answer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    answer = Column(Text, nullable=False)
    correct = Column(Boolean, nullable=False)


class Solution(Base):
    __tablename__ = "solution"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    quiz = Column(UUID(as_uuid=True), ForeignKey("quiz.id"))
    scores = Column(JSONB, nullable=False)
