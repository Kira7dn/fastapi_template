from __future__ import annotations

from typing import List

from app.domain.entities.order import Order


class AvgProcessingTimeService:
    """Calculates average processing time from a list of orders.

    This service assumes each order dict/entity might carry a per-order processing time
    in a field named 'processing_time' on a dict-like structure. Since our domain Order
    does not define it, we accept that consumers will precompute and attach it on
    the objects passed in. We only compute the average over non-negative numeric values.
    """

    @staticmethod
    def compute_avg_time(orders: List[Order]) -> float:
        if not isinstance(orders, list):
            raise ValueError("orders must be a list")
        times: List[float] = []
        for o in orders:
            # allow duck-typing: dict or pydantic Order with attribute
            val = None
            if isinstance(o, dict):
                val = o.get("processing_time")
            else:
                val = getattr(o, "processing_time", None)
            if val is None:
                continue
            if not isinstance(val, (int, float)) or val < 0:
                raise ValueError("processing_time must be non-negative number when provided")
            times.append(float(val))
        if not times:
            return 0.0
        return sum(times) / len(times)
