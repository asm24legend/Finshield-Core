from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

# The engine manages the actual connection pool to Postgres
engine = create_engine(DATABASE_URL)

# Each request gets its own "session" (a workspace for queries/transactions)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All our future SQLAlchemy models will inherit from this Base class
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: gives each request a DB session,
    and guarantees it's closed afterward even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()