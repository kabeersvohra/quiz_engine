from alembic import context
from sqlalchemy import create_engine
from models.base import Base


url = "postgresql://postgres:postgres@128.0.0.1:5432/postgres"
engine = create_engine(url)

config = context.config
target_metadata = Base.metadata

with engine.connect() as connection:
    context.configure(
        connection = connection,
        target_metadata=target_metadata
    )
