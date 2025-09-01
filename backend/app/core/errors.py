from __future__ import annotations

from typing import Any, Mapping, Optional


class ExternalServiceError(Exception):
    """Represents an error returned or raised by an external service/SDK/HTTP.

    Attributes:
        service: Provider/service name (e.g., "stripe", "s3").
        status: Optional HTTP status code when applicable.
        code: Optional provider-specific error code (string).
        details: Optional structured details for debugging/observability.
        original: Optional original exception for chaining.
    """

    def __init__(
        self,
        service: str,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        original: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self.service = service
        self.status = status
        self.code = code
        self.details = dict(details) if details else None
        self.original = original

    def __str__(self) -> str:  # pragma: no cover - formatting convenience
        base = super().__str__()
        bits = [f"[{self.service}] {base}"]
        if self.status is not None:
            bits.append(f"status={self.status}")
        if self.code:
            bits.append(f"code={self.code}")
        return " ".join(bits)
