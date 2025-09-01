from __future__ import annotations

from datetime import datetime
from typing import Any, List

from app.domain.entities.order import Order


class SqlOrderRepository:
    """
    Infrastructure repository skeleton for Order persistence using a SQL database/ORM.

    NOTE: This skeleton intentionally does not implement an application-layer interface yet.
    Add concrete DB session handling and model mapping when the interfaces and models are ready.
    """

    def __init__(self, db_session: Any) -> None:
        self.db_session = db_session

    # ---- CRUD-like operations ----
    def save(self, order: Order) -> Order:
        """Map Order -> OrderModel and persist. Return the persisted domain object."""
        # TODO: Implement mapping to OrderModel and DB persistence
        raise NotImplementedError

    def get_by_id(self, order_id: int) -> Order:
        """Load OrderModel by ID and map to domain Order."""
        # TODO: Implement DB fetch and mapping to Order
        raise NotImplementedError

    def update(self, order: Order) -> None:
        """Update OrderModel with data from the domain Order."""
        # TODO: Implement update logic
        raise NotImplementedError

    # ---- Query helpers ----
    def fetch_orders_by_filters(self, filters: dict) -> List[Order]:
        """Execute query to retrieve orders matching filters."""
        # TODO: Implement filtered query and mapping
        raise NotImplementedError

    def get_orders_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Fetch orders created/updated within the given date range."""
        # TODO: Implement date range query and mapping
        raise NotImplementedError
