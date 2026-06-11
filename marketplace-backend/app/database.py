from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Convert postgresql:// to postgresql+psycopg:// for psycopg v3
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)

# Create engine with connection pooling
engine = create_engine(
    db_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    connect_args={"connect_timeout": 10}
)

# Enable row-level locking for concurrent updates
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Enable PostgreSQL-specific features"""
    #from psycopg import IsolationLevel
    # NOTE: setting isolation level on the raw DB-API connection varies
    # between DB drivers. Avoid calling driver-specific APIs here to
    # remain compatible; we only set a session parameter below.
    cursor = dbapi_conn.cursor()
    cursor.execute("SET SESSION lock_timeout = '10s'")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for DB operations outside of request context"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
