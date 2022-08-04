from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, conlist


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class UserOut(BaseModel):
    id: UUID
    email: str

class SystemUser(UserOut):
    password: str

class QuizOut(BaseModel):
    id: UUID
    name: str

class AnswerSchema(BaseModel):
    answer: str
    correct: bool

class QuestionType(Enum):
    SINGLE = "single"
    MULTI = "multi"

class QuestionSchema(BaseModel):
    question: str
    type: QuestionType
    answers: conlist(AnswerSchema, min_items=1, max_items=5)

class QuizCreate(BaseModel):
    name: str
    questions: conlist(QuestionSchema, min_items=1, max_items=10)
