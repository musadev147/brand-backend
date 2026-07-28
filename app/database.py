"""
Brand Bridge — Database Engine & Session Management
SQLAlchemy 2.0 with sync engine.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.config import get_settings

settings = get_settings()

# ── Engine Setup ──────────────────────────────────────────────
# SQLite needs connect_args for multi-thread access
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,  # SQL logging in dev
)

# Enable WAL mode and foreign keys for SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


# ── Session Factory ───────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Base Model ────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# ── Dependency ────────────────────────────────────────────────
def get_db() -> Session:
    """
    FastAPI dependency that yields a database session.
    Auto-closes after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
