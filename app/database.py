from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# The "engine" is the object that actually manages connections to MySQL.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# A "session" is a temporary workspace for talking to the DB
# (querying, adding, updating, deleting rows) within a single request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Every SQLAlchemy model we create later (Patient, Doctor, etc.)
# will inherit from this Base class, which is how SQLAlchemy
# keeps track of all your tables.
Base = declarative_base()


def get_db():
    """
    This is a FastAPI "dependency" — a reusable function that
    provides a fresh DB session to any route that needs one,
    and guarantees it's closed afterward (even if an error happens).
    We'll use this constantly starting next phase.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
