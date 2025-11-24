from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.config.settings import Settings

def build_engine(settings: Settings) -> Engine:
    """Create a SQLAlchemy engine using application settings."""
    return create_engine(
        settings.database_url.unicode_string(),
        echo=False,
        future=True,
    )

def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a configured session factory bound to the provided engine."""
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )

@contextmanager
def get_session(factory: sessionmaker[Session]) -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_session(factory: sessionmaker[Session]) -> Session:
    """Instantiate a session from the provided session factory."""
    return factory()
