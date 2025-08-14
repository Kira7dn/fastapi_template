from sqlalchemy import Column, Integer, String, ARRAY
from sqlalchemy.orm import Session
from app.application.interfaces.user import UserRepositoryInterface
from app.domain.entities.user import User
from app.infrastructure.database.base import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    preferences = Column(ARRAY(String))  # Cho AI data


class UserRepository(UserRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        db_user = UserModel(
            name=user.name, email=user.email, preferences=user.preferences
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        # Trả về Pydantic User
        return User(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            preferences=db_user.preferences,
        )

    def get_by_id(self, user_id: int) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            return User(
                id=db_user.id,
                name=db_user.name,
                email=db_user.email,
                preferences=db_user.preferences,
            )
        raise ValueError("User not found")

    def get_all(self) -> list[User]:
        db_users = self.db.query(UserModel).all()
        return [
            User(id=u.id, name=u.name, email=u.email, preferences=u.preferences)
            for u in db_users
        ]
