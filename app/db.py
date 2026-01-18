from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = None
SessionLocal = None

Base = declarative_base()

def init_db():
    global engine, SessionLocal

    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
