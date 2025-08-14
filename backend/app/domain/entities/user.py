from pydantic import BaseModel, EmailStr, field_validator


class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    preferences: list[str]

    @field_validator("preferences")
    @classmethod
    def validate_preferences(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Preferences cannot be empty")
        return v
