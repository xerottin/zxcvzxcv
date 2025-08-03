import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud.basket import get_baskets
from models.order import Order, OrderItem, OrderStatus
from schemas.order import OrderCreate
from services.order import generate_order_id

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
            branch_id= payload.branch_id,
            status=OrderStatus.PENDING,
            total_amount=user_baskets["total_count"]
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
                total_price=basket.menu_item.price * basket.quantity
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
        

