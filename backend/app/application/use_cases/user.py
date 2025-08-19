from app.application.interfaces.user import IUserRepository
from app.domain.entities.user import User
from app.domain.services.user import RecommendationService


class CreateUserUseCase:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    def execute(self, name: str, email: str, preferences: list[str]) -> User:
        # Validate với Pydantic
        user_data = {"id": 0, "name": name, "email": email, "preferences": preferences}
        user = User(**user_data)  # Pydantic sẽ validate tự động
        return self.repo.create(user)


class RecommendUsersUseCase:
    def __init__(self, repo: IUserRepository):
        self.repo = repo
        self.rec_service = RecommendationService()

    def execute(self, user_id: int) -> list[str]:
        user = self.repo.get_by_id(user_id)
        all_users = self.repo.get_all()
        return self.rec_service.recommend(user, all_users)
