from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database.base import SessionLocal
from app.infrastructure.repositories.user import UserRepository


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_repo(db: Session = Depends(get_db)):
    return UserRepository(db)
