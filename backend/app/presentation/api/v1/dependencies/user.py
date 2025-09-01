from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.infrastructure.repositories.user import UserRepository
from app.application.interfaces.user import IUserRepository

def get_user_repo(db: Session = Depends(get_db)) -> IUserRepository:
    """Khởi tạo UserRepository từ Session được inject.

    Dependency này giữ presentation layer độc lập với hạ tầng DB,
    giúp dễ test/override trong unit test.
    """
    return UserRepository(db)
