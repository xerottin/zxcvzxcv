import stripe
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from services.payment import (
    create_payment_intent,
    get_payment_by_order_id,
    handle_payment_webhook
)
from schemas.payment import PaymentIntentCreate, PaymentIntentResponse, PaymentResponse
from dependencies.auth import get_current_user
from models.user import User
from db.session import get_pg_db
from core.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

stripe.api_key = "https://buy.stripe.com/test_3cIdR3dYe7rd6oK7UG57W00"

@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
async def create_payment_intent_endpoint(
    payload: PaymentIntentCreate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    """Create a payment intent for an order"""
    payment = await create_payment_intent(db, payload, current_user.id)
    
    return PaymentIntentResponse(
        id=payment.id,
        order_id=payment.order_id,
        stripe_payment_intent_id=payment.stripe_payment_intent_id,
        client_secret=payment.stripe_client_secret,
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        created_at=payment.created_at
    )


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order_endpoint(
    order_id: int,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment information for an order"""
    payment = await get_payment_by_order_id(db, order_id)
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found for this order")
    
    # Check if user owns the order
    if payment.order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return payment


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_pg_db),
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhooks"""
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    
    try:
        payload = await request.body()
        
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        if event["type"].startswith("payment_intent."):
            await handle_payment_webhook(
                db,
                event["type"],
                event["data"]["object"]
            )
        
        return {"status": "success"}
        
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/config")
async def get_stripe_config_endpoint():
    """Get Stripe publishable key for frontend"""
    return {
        "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        "success_url": settings.STRIPE_SUCCESS_URL,
        "cancel_url": settings.STRIPE_CANCEL_URL
    }
