from __future__ import annotations

from typing import List

from app.domain.entities.audit_log_entry import AuditLogEntry


class DynamoAuditLogRepository:
    """
    Infrastructure repository skeleton for AuditLog persistence using DynamoDB (or a similar KV/NoSQL store).

    NOTE: This skeleton intentionally does not implement an application-layer interface yet.
    Add concrete client handling, table config, and mapping when interfaces and infra wiring are ready.
    """

    def __init__(self, table_name: str) -> None:
        self.table_name = table_name
        # self.client = ...  # TODO: inject actual DynamoDB client

    def save(self, log: AuditLogEntry) -> None:
        """Insert AuditLogEntry record into DynamoDB."""
        # TODO: Implement put_item with proper serialization
        raise NotImplementedError

    def get_audit_logs(self, criteria: dict) -> List[AuditLogEntry]:
        """Query DynamoDB for audit logs matching criteria."""
        # TODO: Implement query/scan and mapping to domain entities
        raise NotImplementedError
