import pytest
import mock
import testing.postgresql
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import close_all_sessions, sessionmaker
import app
import deps

from typing import List

from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import RevisionStep
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine


def upgrade_head(engine: Engine) -> None:
    revision = "head"
    alembic_config = AlembicConfig("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", str(engine.url))
    script = ScriptDirectory.from_config(alembic_config)

    def upgrade(rev, context) -> List[RevisionStep]:
        return script._upgrade_revs(revision, rev)

    with EnvironmentContext(
        alembic_config,
        script,
        fn=upgrade,
        destination_rev=revision,
    ) as context:
        with engine.connect() as conn:
            context.configure(connection=conn)
            with context.begin_transaction():
                context.run_migrations()


@pytest.fixture
def db_url() -> str:
    postgresql = testing.postgresql.Postgresql()
    yield "postgresql://{user}@{host}:{port}".format(**postgresql.dsn())

    postgresql.stop()


@pytest.fixture
def engine(db_url: str) -> Engine:
    e = create_engine(db_url, pool_size=50, max_overflow=-1)

    upgrade_head(e)
    yield e

    close_all_sessions()
    e.dispose()


@pytest.fixture(autouse=True)
def patch_db(engine: Engine) -> None:
    patch = mock.patch("app.Session", sessionmaker(bind=engine))
    patch.__enter__()
    patch = mock.patch("deps.Session", sessionmaker(bind=engine))
    patch.__enter__()


@pytest.fixture
def session(engine: Engine) -> Session:
    s = Session(bind=engine)
    yield s

    s.close()
