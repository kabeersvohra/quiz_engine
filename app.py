from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.graphql import GraphQLApp
from starlette.requests import Request
import graphene
from query import Query
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from schemas import UserOut, UserAuth, TokenSchema, SystemUser
from utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from uuid import uuid4
from deps import get_current_user
from models import User

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
Session = sessionmaker(bind=engine, autoflush=False)

app = FastAPI()
router = APIRouter()

schema = graphene.Schema(query=Query)
graphql_app = GraphQLApp(schema=schema)


@router.get("/")
async def status():
    return {"status": "OK"}


@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    # querying database to check if user already exist
    session = Session()
    user = session.query(User).filter_by(email=data.email).first()
    if user is not None:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exist"
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


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(data: UserAuth):
    session = Session()
    user = session.query(User).filter_by(email=data.email).first()
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(data.password, hashed_pass):
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    
    session.close()
    return TokenSchema(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )


@app.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user

app.include_router(router)
