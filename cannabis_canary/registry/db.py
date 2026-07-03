"""Engine/session factory. SQLite for dev/tests; PostgreSQL in production."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from cannabis_canary.registry.models import Base


def create_session_factory(database_url: str) -> tuple[sessionmaker[Session], Engine]:
    kwargs: dict = {}
    if database_url.startswith("sqlite"):
        # The web server handles requests on worker threads; SQLite connections
        # must be shareable across them. ":memory:" additionally needs a single
        # shared connection or every checkout would see an empty database.
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in database_url:
            kwargs["poolclass"] = StaticPool
    engine = create_engine(database_url, **kwargs)
    return sessionmaker(bind=engine, expire_on_commit=False), engine


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
