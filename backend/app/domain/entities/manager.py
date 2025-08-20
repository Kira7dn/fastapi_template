from __future__ import annotations

from pydantic import BaseModel, field_validator


class Manager(BaseModel):
    model_config = {"extra": "forbid", "validate_assignment": True}

    id: int
    role: str

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: int) -> int:
        if v < 1:
            raise ValueError("id must be positive")
        return v

    @field_validator("role")
    @classmethod
    def _validate_role(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("role must be non-empty string")
        allowed = {"manager", "staff"}
        if v not in allowed:
            raise ValueError(f"Invalid role: {v}")
        return v
