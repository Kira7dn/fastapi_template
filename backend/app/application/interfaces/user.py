from abc import ABC, abstractmethod
from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User:
        pass

    @abstractmethod
    def get_all(self) -> list[User]:
        pass
