from __future__ import annotations

from typing import Dict, List

from app.domain.entities.order import Order


class OrdersPerStaffService:
    """Calculates number of orders processed per staff member.

    Counts orders where `staff_id` is set, grouping by `staff_id`.
    """

    @staticmethod
    def compute_throughput(orders: List[Order]) -> Dict[int, int]:
        if not isinstance(orders, list):
            raise ValueError("orders must be a list")
        result: Dict[int, int] = {}
        for o in orders:
            staff_id = None
            if isinstance(o, dict):
                staff_id = o.get("staff_id")
            else:
                staff_id = getattr(o, "staff_id", None)
            if staff_id is None:
                continue
            if not isinstance(staff_id, int) or staff_id < 0:
                raise ValueError("staff_id must be a non-negative integer when provided")
            result[staff_id] = result.get(staff_id, 0) + 1
        return result
