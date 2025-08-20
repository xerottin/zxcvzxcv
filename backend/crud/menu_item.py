import logging
from typing import Optional

from fastapi import HTTPException, status
from models.menu import MenuItem, Menu
from schemas.menu_item import MenuItemCreate, MenuItemUpdate
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


async def create_menu_item(
        db: AsyncSession,
        data: MenuItemCreate,
        current_user_id: Optional[int] = None
) -> MenuItem:
    try:
        menu_query = select(Menu).where(
            Menu.id == data.menu_id,
            Menu.is_active == True
        )
        result = await db.execute(menu_query)
        menu = result.scalar_one_or_none()

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active menu with ID {data.menu_id} not found"
            )

        existing_item_query = select(MenuItem).where(
            MenuItem.menu_id == data.menu_id,
            MenuItem.username == data.username,
            MenuItem.is_active == True
        )
        existing_result = await db.execute(existing_item_query)
        existing_item = existing_result.scalar_one_or_none()

        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item with name '{data.username}' already exists in this menu"
            )

        new_menu_item = MenuItem(
            username=data.username.strip(),
            description=data.description.strip() if data.description else None,
            price=data.price,
            logo=data.logo,
            is_available=data.is_available,
            menu_id=data.menu_id
        )

        db.add(new_menu_item)
        await db.commit()
        await db.refresh(new_menu_item)

        logger.info(
            f"Menu item created successfully: {new_menu_item.id} "
            f"by user {current_user_id}"
        )

        return new_menu_item

    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error creating menu item: {str(e)}")

        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data uniqueness constraint violation"
            )
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid menu reference"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity constraint violation"
            )

    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error creating menu item: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating menu item"
        )


async def get_menu_item(db: AsyncSession, menu_item_id: int) -> Optional[MenuItem]:
    try:
        query = (
            select(MenuItem)
            .options(selectinload(MenuItem.menu))
            .where(MenuItem.id == menu_item_id, MenuItem.is_active == True)
        )
        result = await db.execute(query)
        menu_item = result.scalar_one_or_none()

        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu item with ID {menu_item_id} not found"
            )

        return menu_item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching menu item {menu_item_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving menu item"
        )


async def update_menu_item(
        db: AsyncSession,
        menu_item_id: int,
        data: MenuItemUpdate,
        current_user_id: Optional[int] = None
) -> MenuItem:
    try:
        menu_item = await get_menu_item(db, menu_item_id)

        if data.username and data.username != menu_item.username:
            existing_item_query = select(MenuItem).where(
                MenuItem.menu_id == menu_item.menu_id,
                MenuItem.username == data.username,
                MenuItem.is_active == True,
                MenuItem.id != menu_item_id
            )
            existing_result = await db.execute(existing_item_query)
            existing_item = existing_result.scalar_one_or_none()

            if existing_item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Menu item with username '{data.username}' already exists in this menu"
                )

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['username', 'description'] and value:
                value = value.strip()
            setattr(menu_item, field, value)

        await db.commit()
        await db.refresh(menu_item)

        logger.info(
            f"Menu item updated successfully: {menu_item.id} "
            f"by user {current_user_id}"
        )

        return menu_item

    except HTTPException:
        await db.rollback()
        raise
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error updating menu item: {str(e)}")

        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data uniqueness constraint violation"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity constraint violation"
            )
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error updating menu item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating menu item"
        )


async def patch_menu_item(
        db: AsyncSession,
        menu_item_id: int,
        data: MenuItemUpdate,
        current_user_id: Optional[int] = None
) -> MenuItem:
    return await update_menu_item(db, menu_item_id, data, current_user_id)


async def delete_menu_item(
        db: AsyncSession,
        menu_item_id: int,
        current_user_id: Optional[int] = None
):
    try:
        menu_item = await get_menu_item(db, menu_item_id)

        if menu_item.is_active:
            menu_item.is_active = False
            await db.commit()
            await db.refresh(menu_item)

            logger.info(
                f"Menu item soft deleted successfully: {menu_item.id} "
                f"by user {current_user_id}"
            )

        return {"success": True, "message": "Menu item deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error deleting menu item {menu_item_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while deleting menu item"
        )
