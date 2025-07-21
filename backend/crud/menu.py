# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from models.branch import Menu, MenuItem
from typing import Optional
import logging

from schemas.menu import MenuCreate, MenuItemCreate

logger = logging.getLogger(__name__)




async def create_branch_menu(db: AsyncSession, data: MenuCreate) -> Menu:

    try:
        # Validate that branch exists
        from models.branch import Branch  # Импортируем Branch
        branch_query = select(Branch).where(Branch.id == data.branch_id)
        branch_result = await db.execute(branch_query)
        branch = branch_result.scalar_one_or_none()

        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch with ID {data.branch_id} not found"
            )

        new_menu = Menu(
            name=data.name.strip(),
            logo=data.logo,
            branch_id=data.branch_id
        )

        db.add(new_menu)
        await db.commit()
        await db.refresh(new_menu)

        logger.info(f"Menu created successfully: {new_menu.id}")
        return new_menu

    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error creating menu: {str(e)}")

        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Menu with this name already exists"
            )
        elif "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid branch reference"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating menu due to data constraints"
            )

    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error creating menu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while creating menu"
        )


async def create_menu_item_crud(
        db: AsyncSession,
        data: MenuItemCreate,
        current_user_id: Optional[int] = None
) -> MenuItem:

    try:
        # Validate menu exists and is active
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
            MenuItem.name == data.name,
            MenuItem.is_active == True
        )
        existing_result = await db.execute(existing_item_query)
        existing_item = existing_result.scalar_one_or_none()

        if existing_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item with name '{data.name}' already exists in this menu"
            )

        new_menu_item = MenuItem(
            name=data.name.strip(),
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
        elif "foreign key constraint" in str(e).lower():
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
