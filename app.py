import json
import statistics
from typing import List
from uuid import uuid4

import graphene
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.graphql import GraphQLApp

from deps import get_current_user
from models import Answer, Question, Quiz, Solution, User
from query import Query
from schemas import (
    AnswerOutput,
    AnswerSchema,
    QuestionOutput,
    QuestionSchema,
    QuestionType,
    QuizCreate,
    QuizEdit,
    QuizId,
    QuizOut,
    QuizOutput,
    SolutionCreate,
    SolutionResult,
    SystemUser,
    TokenSchema,
    UserAuth,
    UserOut,
)
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


@app.post("/create/quiz", summary="Create a quiz", response_model=QuizOut)
async def create_quiz(quiz: QuizCreate, user: SystemUser = Depends(get_current_user)):
    session = Session()

    db_quiz = Quiz(id=uuid4(), name=quiz.name, owner=user.id, published=False)
    db_questions = []
    for question in quiz.questions:
        number_of_correct_answers = len([a for a in question.answers if a.correct])
        if (
            question.type == QuestionType.SINGLE and number_of_correct_answers != 1
        ) or (question.type == QuestionType.MULTI and number_of_correct_answers < 1):
            raise HTTPException(
                status_code=400, detail="Incorrect number of correct answers"
            )

        db_answers = []
        for answer in question.answers:
            db_answers.append(Answer(answer=answer.answer, correct=answer.correct))
        db_questions.append(
            Question(
                question=question.question, type=question.type.value, answers=db_answers
            )
        )
    db_quiz.questions = db_questions
    res = QuizOut(
        id=db_quiz.id,
        name=db_quiz.name,
        published=db_quiz.published,
    )
    session.add(db_quiz)
    session.commit()
    session.close()

    return res


@app.get("/view/quiz", summary="See quiz", response_model=QuizOutput)
async def get_quiz(quiz_id: QuizId, user: SystemUser = Depends(get_current_user)):
    session = Session()
    quiz = session.query(Quiz).get(quiz_id.id)
    questions = quiz.questions
    res_questions = [
        QuestionOutput(
            id=q.id,
            question=q.question,
            type=q.type,
            answers=[AnswerOutput(answer=a.answer) for a in q.answers],
        )
        for q in questions
    ]
    res = QuizOutput(name=quiz.name, questions=res_questions)

    session.close()
    return res


@app.get("/list/quiz/mine", summary="", response_model=List[QuizOut])
async def list_my_quiz(user: SystemUser = Depends(get_current_user)):
    session = Session()
    res = session.query(Quiz).filter_by(owner=user.id)
    session.close()
    return [QuizOut(id=q.id, name=q.name, published=q.published) for q in res]


@app.get("/list/quiz/todo", summary="", response_model=List[QuizOut])
async def list_todo_quiz(user: SystemUser = Depends(get_current_user)):
    session = Session()
    quizzes = session.query(Quiz).filter(Quiz.owner != user.id, Quiz.published == True)
    res = [QuizOut(id=q.id, name=q.name, published=q.published) for q in quizzes]
    session.close()
    return res


@app.post("/create/solution", summary="Answer a quiz", response_model=SolutionResult)
async def create_solution(
    solution: SolutionCreate, user: SystemUser = Depends(get_current_user)
):
    session = Session()

    if session.query(Solution).filter(Solution.user == user.id, Solution.quiz == solution.quiz_id).first() is not None:
        raise HTTPException(status_code=400, detail="Quiz has already been completed")

    quiz = session.query(Quiz).filter(Quiz.id == solution.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=400, detail="No such quiz exists")
    elif not quiz.published or quiz.id == user.id:
        raise HTTPException(status_code=400, detail="Quiz cannot be taken, it is your own")

    answer_ids = {a.question_id for a in solution.answers}
    question_ids = {q.id for q in quiz.questions}
    if not answer_ids.issubset(question_ids):
        raise HTTPException(
            status_code=400, detail="Answers do not relate to selected quiz"
        )

    scores = [0.0] * len(quiz.questions)
    for i, question in enumerate(quiz.questions):
        if question.id not in answer_ids:
            continue

        solution_answer = [a for a in solution.answers if a.question_id == question.id][0]

        if (
            question.type == QuestionType.SINGLE.value and len(solution_answer.indices) != 1
        ) or (
            question.type == QuestionType.MULTI.value
            and not 0 < len(solution_answer.indices) < len(question.answers)
        ):
            raise HTTPException(status_code=400, detail="Question answered incorrectly")

        try:
            c_weight = 1.0 / len([a for a in question.answers if a.correct])
        except ZeroDivisionError:
            c_weight = 1.0

        try:
            w_weight = 1.0 / len([a for a in question.answers if not a.correct])
        except ZeroDivisionError:
            w_weight = 1.0

        for j, answer in enumerate(question.answers):
            if answer.correct:
                if j in solution_answer.indices:
                    scores[i] += c_weight
            else:
                if j in solution_answer.indices:
                    scores[i] -= w_weight

    solution = Solution(
        user=user.id,
        quiz=solution.quiz_id,
        scores=json.dumps(scores),
    )

    session.add(solution)
    res = SolutionResult(scores=scores, total_score=statistics.mean(scores))
    session.commit()
    session.close()

    return res


@app.put("/publish/quiz", summary="", response_model=QuizOut)
async def publish_quiz(quiz_id: QuizId, user: SystemUser = Depends(get_current_user)):
    session = Session()
    q = session.query(Quiz).filter_by(owner=user.id, id=quiz_id.id).first()
    if not q:
        raise HTTPException(status_code=400, detail="No such quiz exists")
    if q.published:
        raise HTTPException(status_code=400, detail="Quiz is already published")

    q.published = True
    res = QuizOut(id=q.id, name=q.name, published=q.published)
    session.commit()
    session.close()
    return res


@app.post("/delete/quiz", summary="Delete a quiz", response_model=QuizOut)
async def delete_quiz(quiz_id: QuizId, user: SystemUser = Depends(get_current_user)):
    session = Session()
    q = session.query(Quiz).filter_by(owner=user.id, id=quiz_id.id).first()
    if not q:
        raise HTTPException(status_code=400, detail="No such quiz exists")
    res = QuizId(id=q.id)

    session.delete(q)
    session.commit()
    session.close()
    return res


@app.post("/edit/quiz", summary="Edit a quiz", response_model=QuizOut)
async def edit_quiz(quiz: QuizEdit, user: SystemUser = Depends(get_current_user)):
    session = Session()
    q = session.query(Quiz).filter_by(owner=user.id, id=quiz.id).first()
    if not q:
        raise HTTPException(status_code=400, detail="No such quiz exists")
    if q.published:
        raise HTTPException(status_code=400, detail="Quiz is already published")

    await delete_quiz(QuizId(id=quiz.id), user)
    res = await create_quiz(quiz.new_quiz, user)
    session.commit()
    session.close()
    return res


app.include_router(router)
