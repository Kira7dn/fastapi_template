from app.core.config import settings
from app.application.interfaces.payment import IPaymentGateway
from app.infrastructure.adapters.payment import StripeClient


def get_stripe_client() -> IPaymentGateway:
    # Raise clear error if not configured
    client = StripeClient(api_key=settings.STRIPE_SECRET_KEY)
    return client
