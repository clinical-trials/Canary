"""Engine/session factory. SQLite for dev/tests; PostgreSQL in production."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from cannabis_canary.registry.models import Base


def create_session_factory(database_url: str) -> tuple[sessionmaker[Session], Engine]:
    engine = create_engine(database_url)
    return sessionmaker(bind=engine, expire_on_commit=False), engine


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
