from __future__ import annotations

from typing import Any

from app.domain.entities.packaging_audit import PackagingAudit


class SQLPackagingAuditRepository:
    """
    Infrastructure repository skeleton for PackagingAudit persistence using a SQL database/ORM.

    NOTE: This skeleton intentionally does not implement an application-layer interface yet.
    Add concrete DB session handling and model mapping when the interfaces and models are ready.
    """

    def __init__(self, db_session: Any) -> None:
        self.db_session = db_session

    def save(self, audit: PackagingAudit) -> None:
        """Insert PackagingAuditModel record into database."""
        # TODO: Implement mapping to PackagingAuditModel and DB persistence
        raise NotImplementedError
