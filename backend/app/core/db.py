from typing import Generator
from sqlalchemy.orm import Session
from app.infrastructure.database.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Per-request SQLAlchemy Session lifecycle.

    - Open session before handling the endpoint
    - Ensure session is closed after handling (even on exception)
    - Commit/Rollback should be controlled in use cases or a unit of work
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
