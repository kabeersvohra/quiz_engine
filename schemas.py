from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, conlist


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    email: str = Field(..., description="user email") # email validation should be done here
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class UserOut(BaseModel):
    id: UUID
    email: str


class SystemUser(UserOut):
    password: str


class QuizOut(BaseModel):
    id: UUID
    name: str
    published: bool


class SolutionOut(BaseModel):
    quiz_id: UUID
    quiz_name: str
    completed_by: str
    scores: List[float]
    total_score: float


class AnswerSchema(BaseModel):
    answer: str
    correct: Optional[bool]


class QuestionType(Enum):
    SINGLE = "single"
    MULTI = "multi"


class QuestionSchema(BaseModel):
    question: str
    type: QuestionType
    answers: conlist(AnswerSchema, min_items=1, max_items=5)


class SolutionResult(BaseModel):
    scores: List[float]
    total_score: float


class SolutionAnswer(BaseModel):
    question_id: UUID
    indices: List[int]


class SolutionCreate(BaseModel):
    quiz_id: UUID
    answers: List[SolutionAnswer]


class QuizCreate(BaseModel):
    name: str
    questions: conlist(QuestionSchema, min_items=1, max_items=10)


class QuizEdit(BaseModel):
    id: UUID
    new_quiz: QuizCreate


class QuizId(BaseModel):
    id: UUID

class AnswerOutput(BaseModel):
    answer: str

class QuestionOutput(BaseModel):
    id: UUID
    question: str
    type: QuestionType
    answers: List[AnswerOutput]

class QuizOutput(BaseModel):
    name: str
    questions: List[QuestionOutput]
