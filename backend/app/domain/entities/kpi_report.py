from __future__ import annotations

from pydantic import BaseModel, field_validator


class KpiReport(BaseModel):
    model_config = {"extra": "forbid", "validate_assignment": True}

    throughput_per_staff: dict
    avg_handling_time: float

    @field_validator("throughput_per_staff")
    @classmethod
    def _validate_throughput(cls, v: dict) -> dict:
        if not isinstance(v, dict):
            raise ValueError("throughput_per_staff must be a dict")
        for key, val in v.items():
            # Keys must be integers (staff ids)
            if not isinstance(key, int):
                raise ValueError("throughput_per_staff keys must be int")
            if not isinstance(val, int) or val < 0:
                raise ValueError("throughput_per_staff values must be non-negative ints")
        return v

    @field_validator("avg_handling_time")
    @classmethod
    def _validate_avg(cls, v: float) -> float:
        if not isinstance(v, (int, float)) or v < 0:
            raise ValueError("avg_handling_time must be non-negative number")
        return float(v)
