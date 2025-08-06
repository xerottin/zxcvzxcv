from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.payment import PaymentStatus, PaymentMethod


class PaymentIntentCreate(BaseModel):
    order_id: int
    currency: str = "USD"


class PaymentIntentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: int
    stripe_payment_intent_id: str
    client_secret: str
    amount: int
    currency: str
    status: PaymentStatus
    created_at: datetime


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: int
    stripe_payment_intent_id: str
    amount: int
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod | None = None
    failure_reason: str | None = None
    receipt_url: str | None = None
    created_at: datetime
    updated_at: datetime


class PaymentWebhookEvent(BaseModel):
    type: str
    data: dict

class PaymentIntentCreate(BaseModel):
    order_id: int
    currency: str | None = None