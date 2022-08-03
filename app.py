from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.graphql import GraphQLApp
from starlette.requests import Request
import graphene
from query import Query

engine = create_engine("postgresql://postgres:postgres@localhost:5432/postgres")
Session = sessionmaker(bind=engine, autoflush=False)

app = FastAPI()
router = APIRouter()

schema = graphene.Schema(query=Query)
graphql_app = GraphQLApp(schema=schema)

@router.get("/")
async def status():
    return {"status": "OK"}

app.include_router(router)
