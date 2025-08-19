from typing import Dict, Any, Optional

from app.application.interfaces.payment import IPaymentGateway
from app.core.config import settings


class StripeNotConfiguredError(RuntimeError):
    pass


class StripeClient(IPaymentGateway):
    """Stripe adapter. Requires STRIPE_SECRET_KEY in env.
    If the stripe SDK is not installed, raise a clear error at first use.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.STRIPE_SECRET_KEY
        if not self.api_key:
            raise StripeNotConfiguredError(
                "STRIPE_SECRET_KEY is missing. Set it in environment."
            )
        # Lazy import so app can start without stripe for non-payment features
        try:
            import stripe  # type: ignore
        except Exception as e:  # pragma: no cover
            raise StripeNotConfiguredError(
                "python-stripe SDK is not installed. Install with `venv/bin/pip install stripe`."
            ) from e
        self._stripe = stripe
        self._stripe.api_key = self.api_key

    def create_payment_intent(
        self,
        amount_cents: int,
        currency: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        pi = self._stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency or settings.STRIPE_DEFAULT_CURRENCY,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True},
        )
        return {
            "id": pi["id"],
            "client_secret": pi.get("client_secret"),
            "status": pi.get("status"),
            "amount": pi.get("amount"),
            "currency": pi.get("currency"),
        }

    def retrieve_payment_intent(self, intent_id: str) -> Dict[str, Any]:
        pi = self._stripe.PaymentIntent.retrieve(intent_id)
        return {
            "id": pi["id"],
            "status": pi.get("status"),
            "amount": pi.get("amount"),
            "currency": pi.get("currency"),
        }

    def construct_webhook_event(
        self, payload: bytes, sig_header: str
    ) -> Dict[str, Any]:
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        if not webhook_secret:
            raise StripeNotConfiguredError(
                "STRIPE_WEBHOOK_SECRET is missing. Set it in environment."
            )
        event = self._stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=webhook_secret
        )
        # Return minimal dict to avoid leaking raw objects
        return {
            "id": event.get("id"),
            "type": event.get("type"),
            "data": event.get("data", {}),
        }
