from __future__ import annotations

from app.domain.entities.manager import Manager


class ManagerAccessService:
    """Validate a manager's access rights.

    Pure logic: return True if the manager has role 'manager', otherwise raise PermissionError.
    """

    @staticmethod
    def validate_access(manager: Manager) -> bool:
        if not isinstance(manager, Manager):
            raise ValueError("manager must be a Manager instance")
        if manager.role != "manager":
            raise PermissionError("Access denied: only managers are allowed")
        return True
