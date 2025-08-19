from fastapi import Depends

from app.core.config import settings
from app.infrastructure.adapters.payment import StripeClient


def get_stripe_client() -> StripeClient:
    # Raise clear error if not configured
    client = StripeClient(api_key=settings.STRIPE_SECRET_KEY)
    return client
