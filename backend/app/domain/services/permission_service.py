from __future__ import annotations


class PermissionService:
    """Validates that a user has manager permissions.

    Pure logic with deterministic outcomes. No I/O.
    """

    @staticmethod
    def validate_manager(user_id: str) -> None:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")
        # Example rule: user IDs starting with 'mgr_' denote managers
        if not user_id.startswith("mgr_"):
            raise PermissionError("User does not have manager permissions")
