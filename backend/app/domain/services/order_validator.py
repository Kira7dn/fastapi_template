from __future__ import annotations

from typing import Dict

from app.domain.entities.order import Order


class OrderValidator:
    """Validates incoming order data and constructs an Order entity."""

    @staticmethod
    def validate(order_data: Dict) -> Order:
        if not isinstance(order_data, dict):
            raise ValueError("order_data must be a dict")
        items = order_data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError("items must be a non-empty list")
        # new order always starts with status 'new'
        return Order(id=int(order_data.get("id", 0)), items=list(items), status="new")
