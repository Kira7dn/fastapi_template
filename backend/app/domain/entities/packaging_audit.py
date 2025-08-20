from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator


class PackagingAudit(BaseModel):
    model_config = {"extra": "forbid", "validate_assignment": True}

    order_id: int
    timestamp: datetime

    @field_validator("order_id")
    @classmethod
    def _validate_order_id(cls, v: int) -> int:
        if v < 1:
            raise ValueError("order_id must be positive")
        return v

    @classmethod
    def create(cls, order_id: int) -> "PackagingAudit":
        # Deterministic timestamp to avoid using system clock in code under test
        return cls(order_id=order_id, timestamp=datetime.fromtimestamp(0))
