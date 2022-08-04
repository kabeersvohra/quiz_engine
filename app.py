from uuid import uuid4

import graphene
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.graphql import GraphQLApp

from deps import get_current_user
from models import Answer, Question, Quiz, User
from query import Query
from schemas import QuestionType, QuizCreate, QuizOut, SystemUser, TokenSchema, UserAuth, UserOut
from utils import (
    create_access_token,
    create_refresh_token,
    get_hashed_password,
    verify_password,
)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
Session = sessionmaker(bind=engine, autoflush=False)

app = FastAPI()
router = APIRouter()

schema = graphene.Schema(query=Query)
graphql_app = GraphQLApp(schema=schema)


@router.get("/")
async def status():
    return {"status": "OK"}


@app.post("/signup", summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    # querying database to check if user already exist
    session = Session()
    user = session.query(User).filter_by(email=data.email).first()
    if user is not None:
        raise HTTPException(
            status_code=400, detail="User with this email already exist"
        )
    user_id = str(uuid4())
    user = User(
        id=user_id,
        email=data.email,
        password=get_hashed_password(data.password),
    )
    session.add(user)
    session.commit()
    session.close()
    return UserOut(id=user_id, email=data.email)


@app.post(
    "/login",
    summary="Create access and refresh tokens for user",
    response_model=TokenSchema,
)
async def login(data: UserAuth):
    session = Session()
    user = session.query(User).filter_by(email=data.email).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    hashed_pass = user.password
    if not verify_password(data.password, hashed_pass):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    session.close()
    return TokenSchema(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@app.get(
    "/me", summary="Get details of currently logged in user", response_model=UserOut
)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user


@app.post(
    "/create", summary="Create a quiz", response_model=QuizOut
)
async def create_quiz(quiz: QuizCreate, user: SystemUser = Depends(get_current_user)):
    session = Session()

    db_quiz = Quiz(name=quiz.name, owner=user.id)
    db_questions = []
    for question in quiz.questions:
        number_of_correct_answers = len([a for a in question.answers if a.correct])
        if (
            (question.type == QuestionType.SINGLE and number_of_correct_answers != 1)
            or
            (question.type == QuestionType.MULTI and number_of_correct_answers < 1)
        ):
            raise HTTPException(status_code=400, detail="Incorrect number of correct answers")

        db_answers = []
        for answer in question.answers:
            db_answers.append(Answer(answer=answer.answer, correct=answer.correct))
        db_questions.append(
            Question(question=question.question, type=question.type.value, answers=db_answers)
        )
    db_quiz.questions = db_questions
    session.add(db_quiz)
    session.commit()
    session.close()

    return QuizOut(
        id=uuid4(),
        name=quiz.name
    )


app.include_router(router)
