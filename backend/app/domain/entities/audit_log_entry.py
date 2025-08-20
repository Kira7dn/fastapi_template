from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class AuditLogEntry(BaseModel):
    model_config = {"extra": "forbid", "validate_assignment": True}

    id: str
    order_id: int
    action: str
    user_id: Optional[str] = None
    staff_id: Optional[int] = None
    timestamp: datetime

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("id must be non-empty string")
        return v

    @field_validator("order_id")
    @classmethod
    def _validate_order_id(cls, v: int) -> int:
        if v < 1:
            raise ValueError("order_id must be positive")
        return v

    @field_validator("action")
    @classmethod
    def _validate_action(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("action must be a non-empty string")
        return v
