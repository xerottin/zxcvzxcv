import logging
from datetime import datetime
from typing import Optional

from crud.basket import get_baskets
from fastapi import HTTPException
from models.order import Order, OrderItem, OrderStatus
from schemas.order import OrderCreate, OrderUpdate
from services.order import generate_order_id
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


async def create_order(db: AsyncSession, payload: OrderCreate):
    try:
        logger.debug(f"Creating order with payload: {payload}")

        user_baskets = await get_baskets(db, payload.user_id)
        if not user_baskets["baskets"]:
            raise HTTPException(status_code=404, detail="No active baskets found for user")

        order_id = generate_order_id()
        order = Order(
            username=order_id,
            special_instructions=payload.special_instructions,
            delivery_address=payload.delivery_address,
            user_id=payload.user_id,
            branch_id=payload.branch_id,
            status=OrderStatus.PENDING,
            total_amount=user_baskets["total_count"],
        )
        db.add(order)
        await db.flush()

        for basket in user_baskets["baskets"]:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=basket.menu_item_id,
                quantity=basket.quantity,
                price=basket.menu_item.price,
                is_active=basket.is_active,
                total_price=basket.menu_item.price * basket.quantity,
            )
            db.add(order_item)
        for basket in user_baskets["baskets"]:
            await db.delete(basket)

        await db.commit()
        await db.refresh(order)

        logger.info(f"Order created with ID: {order.username}")
        return order

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_orders(
    db: AsyncSession, user_id: Optional[int] = None, branch_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> dict:
    try:
        query = (
            select(Order)
            .options(selectinload(Order.order_item).selectinload(OrderItem.menu_item))
            .where(Order.is_active == True)
        )
        if user_id:
            query = query.where(Order.user_id == user_id)

        if branch_id:
            query = query.where(Order.branch_id == branch_id)

        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)

        count_query = select(func.count(Order.id))
        if user_id:
            count_query = count_query.where(Order.user_id == user_id)
        if branch_id:
            count_query = count_query.where(Order.branch_id == branch_id)

        orders = await db.scalars(query)
        total_count = await db.scalar(count_query)

        return {"orders": orders.all(), "total_count": total_count or 0, "skip": skip, "limit": limit}

    except Exception as e:
        logger.error(f"Error getting orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_order(db: AsyncSession, order_id: int, user_id: Optional[int] = None) -> Order:
    try:
        query = (
            select(Order)
            .options(selectinload(Order.order_item).selectinload(OrderItem.menu_item))
            .where(Order.id == order_id, Order.is_active == True)
        )

        if user_id:
            query = query.where(Order.user_id == user_id)

        order = await db.scalar(query)

        if not order:
            raise HTTPException(
                status_code=404, detail="Order not found" if not user_id else "Order not found or access denied"
            )

        return order

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_order(db: AsyncSession, order_id: int, data: OrderUpdate, user_id: Optional[int] = None) -> Order:
    try:
        query = select(Order).where(Order.id == order_id)
        if user_id:
            query = query.where(Order.user_id == user_id)

        order = await db.scalar(query)

        if not order:
            raise HTTPException(
                status_code=404, detail="Order not found" if not user_id else "Order not found or access denied"
            )

        # Validate status transition (optional business logic)
        if hasattr(data, "status") and data.status:
            if not _is_valid_status_transition(order.status, data.status):
                raise HTTPException(
                    status_code=400, detail=f"Invalid status transition from {order.status} to {data.status}"
                )

        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(order, field):
                setattr(order, field, value)

        await db.commit()
        await db.refresh(order)

        updated_order = await get_order(db, order_id, user_id)

        logger.info(f"Order {order_id} updated successfully")
        return updated_order

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


def _is_valid_status_transition(current_status: OrderStatus, new_status: str) -> bool:
    try:
        new_status_enum = OrderStatus(new_status)
    except ValueError:
        return False

    # Define valid transitions
    valid_transitions = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
        OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
        OrderStatus.READY: [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.COMPLETED],
        OrderStatus.OUT_FOR_DELIVERY: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
        OrderStatus.COMPLETED: [],
        OrderStatus.CANCELLED: [],
    }

    return new_status_enum in valid_transitions.get(current_status, [])


async def delete_order(db: AsyncSession, order_id: int, user_id: int = None) -> dict:
    try:
        query = select(Order).where(Order.id == order_id)
        if user_id:
            query = query.where(Order.user_id == user_id)

        order = await db.scalar(query)

        if not order:
            raise HTTPException(
                status_code=404, detail="Order not found" if not user_id else "Order not found or access denied"
            )

        if order.status not in [OrderStatus.PENDING, OrderStatus.CANCELLED, OrderStatus.DELIVERED]:
            raise HTTPException(status_code=400, detail="Only pending or cancelled or delivered orders can be deleted")

        # await db.execute(delete(OrderItem).where(OrderItem.order_id == order_id))
        # await db.delete(order)

        order.is_active = False
        order.update_time = datetime.utcnow()

        await db.commit()

        logger.info(f"Order {order_id} deleted successfully")
        return {"message": f"Order {order_id} deleted successfully"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
