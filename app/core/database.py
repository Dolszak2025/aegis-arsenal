"""Database configuration and session management"""

from typing import Optional, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool, NullPool

from app.core.config import settings

# Create declarative base for models
Base = declarative_base()

# Database URL configuration
DATABASE_URL = settings.DATABASE_URL

# Choose pool based on environment
if settings.ENVIRONMENT == "development":
    # Use NullPool in development for simpler connection handling
    poolclass = NullPool
else:
    # Use QueuePool in production for connection pooling
    poolclass = QueuePool

# Create engine with appropriate pool settings
engine = create_engine(
    DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    poolclass=poolclass,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before using
    connect_args={
        "connect_timeout": 10,
        "application_name": "aegis_arsenal",
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session in FastAPI routes
    
    Usage:
        @app.get("/api/data")
        async def get_data(db: Session = Depends(get_db)):
            return db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_db_async() -> Generator[Session, None, None]:
    """
    Async dependency for getting database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database: create all tables"""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all tables (WARNING: Use only in development)"""
    if settings.ENVIRONMENT == "production":
        raise RuntimeError("Cannot drop database in production!")
    Base.metadata.drop_all(bind=engine)


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configure connection on creation"""
    # Enable UUID type support for PostgreSQL
    if "postgresql" in str(DATABASE_URL):
        dbapi_conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")


# Export for use in models
__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_async",
    "init_db",
    "drop_db",
]
