from typing import Protocol, Optional, Dict, Any


class IPaymentGateway(Protocol):
    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Create a payment intent with amount in cents."""

    def retrieve_payment_intent(self, intent_id: str) -> Dict[str, Any]:
        """Retrieve a payment intent by ID."""

    def construct_webhook_event(
        self, payload: bytes, sig_header: str
    ) -> Dict[str, Any]:
        """Verify and parse a Stripe webhook event payload."""
