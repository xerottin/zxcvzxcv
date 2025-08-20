import logging

from fastapi import HTTPException
from models.basket import Basket
from models.menu import MenuItem
from models.user import User
from schemas.basket import BasketCreateSchema, BasketUpdateSchema
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


async def create_basket(db: AsyncSession, data: BasketCreateSchema, user_id: int) -> Basket:
    try:
        menu_item = await db.scalar(select(MenuItem).where(MenuItem.id == data.menu_item_id))
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        existing_basket = await db.scalar(
            select(Basket)
            .options(selectinload(Basket.menu_item))
            .where(and_(Basket.user_id == user_id, Basket.menu_item_id == data.menu_item_id))
        )

        if existing_basket:
            existing_basket.quantity += data.quantity
            await db.commit()
            await db.refresh(existing_basket)
            return existing_basket

        basket_data = data.dict(exclude_unset=True)
        basket_data["user_id"] = user_id
        basket = Basket(**basket_data)

        db.add(basket)
        await db.commit()
        await db.refresh(basket)

        basket_with_menu = await db.scalar(
            select(Basket).options(selectinload(Basket.menu_item)).where(Basket.id == basket.id)
        )

        return basket_with_menu

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating basket item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_basket(db: AsyncSession, basket_id: int) -> Basket:
    try:
        result = await db.execute(select(Basket).options(selectinload(Basket.menu_item)).where(Basket.id == basket_id))
        basket = result.scalars().first()

        if not basket:
            raise HTTPException(status_code=404, detail="Basket item not found")

        return basket

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting basket item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_baskets(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> dict:
    try:
        result = await db.execute(
            select(Basket)
            .options(selectinload(Basket.menu_item))
            .where(Basket.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Basket.created_at.desc())
        )

        baskets = result.scalars().all()

        total_count = 0
        for basket in baskets:
            if basket.menu_item and basket.menu_item.price:
                total_count += basket.menu_item.price * basket.quantity

        return {"baskets": baskets, "total_count": total_count}

    except Exception as e:
        logger.error(f"Error getting user baskets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_basket(db: AsyncSession, basket_id: int, data: BasketUpdateSchema, user_id: int) -> Basket:
    try:
        basket = await db.scalar(select(Basket).options(selectinload(Basket.menu_item)).where(Basket.id == basket_id))
        if not basket:
            raise HTTPException(status_code=404, detail="Basket item not found")

        if basket.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        if data.menu_item_id != basket.menu_item_id:
            menu_item = await db.scalar(select(MenuItem).where(MenuItem.id == data.menu_item_id))
            if not menu_item:
                raise HTTPException(status_code=404, detail="Menu item not found")

            existing_basket = await db.scalar(
                select(Basket).where(
                    and_(Basket.user_id == user_id, Basket.menu_item_id == data.menu_item_id, Basket.id != basket_id)
                )
            )

            if existing_basket:
                raise HTTPException(status_code=409, detail="Item already exists in basket")

        for key, value in data.dict(exclude_unset=True).items():
            setattr(basket, key, value)

        await db.commit()
        await db.refresh(basket)

        if data.menu_item_id != basket.menu_item_id:
            basket = await db.scalar(
                select(Basket).options(selectinload(Basket.menu_item)).where(Basket.id == basket_id)
            )

        return basket

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating basket item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_patch_basket(db: AsyncSession, basket_id: int, quantity: int, user_id: int) -> Basket:
    try:
        basket = await db.scalar(select(Basket).options(selectinload(Basket.menu_item)).where(Basket.id == basket_id))
        if not basket:
            raise HTTPException(status_code=404, detail="Basket item not found")

        if basket.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if quantity > 99:
            raise HTTPException(status_code=400, detail="Quantity cannot exceed 99")

        basket.quantity = quantity
        await db.commit()
        await db.refresh(basket)
        return basket

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating basket quantity: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_basket(db: AsyncSession, basket_id: int, user_id: int) -> None:
    try:
        basket = await db.scalar(select(Basket).where(Basket.id == basket_id))
        if not basket:
            raise HTTPException(status_code=404, detail="Basket item not found")

        if basket.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        await db.delete(basket)
        await db.commit()

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting basket item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def clear_user_basket(db: AsyncSession, user_id: int) -> None:
    try:
        await db.execute(delete(Basket).where(Basket.user_id == user_id))
        await db.commit()

    except Exception as e:
        await db.rollback()
        logger.error(f"Error clearing user basket: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_basket_total_items(db: AsyncSession, user_id: int) -> int:
    try:
        result = await db.scalar(select(func.sum(Basket.quantity)).where(Basket.user_id == user_id))
        return result or 0

    except Exception as e:
        logger.error(f"Error getting basket total: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
