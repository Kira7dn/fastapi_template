from fastapi import APIRouter, Depends

from app.application.use_cases.user import (
    CreateUserUseCase,
    RecommendUsersUseCase,
)
from app.presentation.api.v1.dependencies.user import get_user_repo
from app.presentation.api.v1.schemas.user import (
    CreateUserRequest,
    RecommendationResponse,
    UserResponse,
)


router = APIRouter()


@router.post("/users/", response_model=UserResponse)
def create_user(request: CreateUserRequest, repo=Depends(get_user_repo)):
    use_case = CreateUserUseCase(repo)
    user = use_case.execute(request.name, request.email, request.preferences)
    return UserResponse.from_orm(user)  # Hoặc user.dict() nếu không dùng from_orm


@router.get("/recommend/{user_id}", response_model=RecommendationResponse)
def recommend(user_id: int, repo=Depends(get_user_repo)):
    use_case = RecommendUsersUseCase(repo)
    recs = use_case.execute(user_id)
    return RecommendationResponse(recommendations=recs)
