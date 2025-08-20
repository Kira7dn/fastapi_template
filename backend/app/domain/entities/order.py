from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator


class Order(BaseModel):
    model_config = {"extra": "forbid", "validate_assignment": True}

    id: int
    items: List
    status: str
    staff_id: Optional[int] = None
    confirmed_at: Optional[datetime] = None
    processing_time: Optional[float] = None

    # ---------- Validators ----------
    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: int) -> int:
        if v < 0:
            raise ValueError("id must be non-negative")
        return v

    @field_validator("items")
    @classmethod
    def _validate_items(cls, v: List) -> List:
        if not isinstance(v, list):
            raise ValueError("items must be a list")
        if len(v) == 0:
            raise ValueError("items cannot be empty")
        return v

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("status must be a non-empty string")
        allowed = {"new", "confirmed", "packaged"}
        if v not in allowed:
            # keep flexible but still deterministic: allow any non-empty status, but flag unexpected
            # Raising to enforce cleanliness per rules
            raise ValueError(f"Invalid status: {v}")
        return v

    @field_validator("processing_time")
    @classmethod
    def _validate_processing_time(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if not isinstance(v, (int, float)) or v < 0:
            raise ValueError("processing_time must be a non-negative number when provided")
        return float(v)

    # ---------- Methods (business rules) ----------
    def validate_data(self, order_data: dict) -> None:
        """Validates incoming order data prior to creation."""
        if not isinstance(order_data, dict):
            raise ValueError("order_data must be a dict")
        items = order_data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError("order_data.items must be a non-empty list")

    def validate_new(self) -> None:
        if self.status != "new":
            raise ValueError("Order must be in 'new' status")

    def assign_to_staff(self, staff_id: int) -> None:
        if staff_id is None or staff_id < 0:
            raise ValueError("staff_id must be a non-negative integer")
        self.staff_id = staff_id

    def confirm(self, timestamp: datetime) -> None:
        if not isinstance(timestamp, datetime):
            raise ValueError("timestamp must be datetime")
        self.status = "confirmed"
        self.confirmed_at = timestamp

    def validate_status(self, expected_status: str) -> None:
        if self.status != expected_status:
            raise ValueError(f"Expected status '{expected_status}', got '{self.status}'")

    def mark_packaged(self) -> None:
        self.status = "packaged"
