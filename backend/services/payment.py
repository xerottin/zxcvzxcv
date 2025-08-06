import stripe
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from models.payment import Payment, PaymentStatus
from models.order import Order, OrderStatus
from schemas.payment import PaymentIntentCreate
from core.settings import settings


logger = logging.getLogger(__name__)

async def create_payment_intent(db: AsyncSession, payload: PaymentIntentCreate, user_id: int) -> Payment:
    """Create a Stripe Payment Intent for an order"""
    try:
        # Проверяем, что Stripe ключи из одной среды (test/live)
        if not settings.stripe_keys_match_env:
            logger.error("Stripe secret and publishable keys are from different environments!")
            raise HTTPException(
                status_code=500, 
                detail="Payment configuration error"
            )

        # Проверяем существование заказа
        query = select(Order).where(
            Order.id == payload.order_id,
            Order.user_id == user_id,
            Order.is_active == True
        )
        order = await db.scalar(query)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found or access denied")
        
        # Проверяем статус заказа
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot create payment for order with status: {order.status}"
            )
        
        # Проверяем существующий платеж
        existing_payment = await get_payment_by_order_id(db, payload.order_id)
        if existing_payment and existing_payment.status == PaymentStatus.SUCCEEDED:
            raise HTTPException(
                status_code=400,
                detail="Payment already completed for this order"
            )
        
        currency = payload.currency or settings.STRIPE_CURRENCY
        
        # Создаем Stripe Payment Intent
        stripe_intent = stripe.PaymentIntent.create(
            amount=order.total_amount,  # Amount in cents
            currency=currency.lower(),
            metadata={
                "order_id": str(order.id),
                "user_id": str(user_id),
                "order_username": order.username,
                "environment": "live" if settings.is_stripe_live_mode else "test"
            },
            automatic_payment_methods={
                "enabled": True
            }
        )
        
        # Создаем или обновляем запись о платеже
        if existing_payment:
            existing_payment.stripe_payment_intent_id = stripe_intent.id
            existing_payment.stripe_client_secret = stripe_intent.client_secret
            existing_payment.amount = order.total_amount
            existing_payment.currency = currency
            existing_payment.status = PaymentStatus.PENDING
            payment = existing_payment
        else:
            payment = Payment(
                order_id=order.id,
                stripe_payment_intent_id=stripe_intent.id,
                amount=order.total_amount,
                currency=currency,
                status=PaymentStatus.PENDING,
                stripe_client_secret=stripe_intent.client_secret
            )
            db.add(payment)
        
        await db.commit()
        await db.refresh(payment)
        
        logger.info(f"Payment intent created for order {order.id}: {stripe_intent.id}")
        return payment
        
    except HTTPException:
        await db.rollback()
        raise
    except stripe.error.StripeError as e:
        await db.rollback()
        logger.error(f"Stripe error creating payment intent: {e}")
        raise HTTPException(status_code=400, detail=f"Payment processing error: {str(e)}")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating payment intent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_payment_by_order_id(db: AsyncSession, order_id: int) -> Optional[Payment]:
    """Get payment by order ID"""
    try:
        query = select(Payment).where(Payment.order_id == order_id)
        return await db.scalar(query)
    except Exception as e:
        logger.error(f"Error getting payment for order {order_id}: {e}")
        return None


async def get_payment_by_intent_id(db: AsyncSession, intent_id: str) -> Optional[Payment]:
    """Get payment by Stripe Payment Intent ID"""
    try:
        query = select(Payment).options(
            selectinload(Payment.order)
        ).where(Payment.stripe_payment_intent_id == intent_id)
        return await db.scalar(query)
    except Exception as e:
        logger.error(f"Error getting payment for intent {intent_id}: {e}")
        return None


async def update_payment_status(
    db: AsyncSession,
    payment: Payment,
    status: PaymentStatus,
    failure_reason: Optional[str] = None,
    receipt_url: Optional[str] = None
) -> Payment:
    """Update payment status and related order status"""
    try:
        payment.status = status
        if failure_reason:
            payment.failure_reason = failure_reason
        if receipt_url:
            payment.receipt_url = receipt_url
        
        # Обновляем статус заказа в зависимости от статуса платежа
        if status == PaymentStatus.SUCCEEDED:
            payment.order.status = OrderStatus.CONFIRMED
        elif status == PaymentStatus.FAILED:
            payment.order.status = OrderStatus.CANCELLED
        elif status == PaymentStatus.CANCELLED:
            payment.order.status = OrderStatus.CANCELLED
        
        await db.commit()
        await db.refresh(payment)
        
        logger.info(
            f"Payment {payment.id} status updated to {status}, "
            f"order {payment.order_id} status updated to {payment.order.status}"
        )
        return payment
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating payment status: {e}", exc_info=True)
        raise


async def handle_payment_webhook(db: AsyncSession, event_type: str, payment_intent_data: dict):
    """Handle Stripe webhook events"""
    try:
        intent_id = payment_intent_data.get("id")
        if not intent_id:
            logger.warning("No payment intent ID in webhook data")
            return
        
        payment = await get_payment_by_intent_id(db, intent_id)
        if not payment:
            logger.warning(f"Payment not found for intent ID: {intent_id}")
            return
        
        # Логируем среду выполнения для отладки
        metadata = payment_intent_data.get("metadata", {})
        env = metadata.get("environment", "unknown")
        logger.info(f"Processing webhook for {env} environment: {event_type}")
        
        if event_type == "payment_intent.succeeded":
            await update_payment_status(
                db,
                payment,
                PaymentStatus.SUCCEEDED,
                receipt_url=payment_intent_data.get("charges", {}).get("data", [{}])[0].get("receipt_url")
            )
        elif event_type == "payment_intent.payment_failed":
            failure_reason = payment_intent_data.get("last_payment_error", {}).get("message", "Payment failed")
            await update_payment_status(
                db,
                payment,
                PaymentStatus.FAILED,
                failure_reason=failure_reason
            )
        elif event_type == "payment_intent.canceled":
            await update_payment_status(db, payment, PaymentStatus.CANCELLED)
        elif event_type == "payment_intent.processing":
            await update_payment_status(db, payment, PaymentStatus.PROCESSING)
        
        logger.info(f"Webhook processed: {event_type} for payment {payment.id}")
        
    except Exception as e:
        logger.error(f"Error handling webhook {event_type}: {e}", exc_info=True)
        raise