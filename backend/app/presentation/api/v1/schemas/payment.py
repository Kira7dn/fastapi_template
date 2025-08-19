from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CreatePaymentIntentRequest(BaseModel):
    amount_cents: int = Field(..., ge=1, description="Amount in cents")
    currency: Optional[str] = Field(None, description="ISO currency code, default from settings")
    metadata: Optional[Dict[str, str]] = None


class PaymentIntentResponse(BaseModel):
    id: str
    client_secret: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[int] = None
    currency: Optional[str] = None


class WebhookAcknowledgeResponse(BaseModel):
    received: bool = True
    event_id: Optional[str] = None
    event_type: Optional[str] = None
