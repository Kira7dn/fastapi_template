from pydantic import BaseModel, ConfigDict
from typing import List


class CreateUserRequest(BaseModel):
    name: str
    email: str
    preferences: List[str]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    preferences: List[str]


class RecommendationResponse(BaseModel):
    recommendations: List[str]
