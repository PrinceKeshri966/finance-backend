from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# check_same_thread is a SQLite-only requirement
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency that yields a DB session.
    The finally block ensures the session is always closed,
    even if an exception is raised during the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
