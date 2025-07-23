from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete as sql_delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import logging
from typing import List, Optional

from models.menu import Menu
from models.branch import Branch
from schemas.menu import MenuCreate, MenuUpdate, MenuPatch

logger = logging.getLogger(__name__)


async def create_menu(db: AsyncSession, data: MenuCreate) -> Menu:
    try:
        branch_query = select(Branch).where(Branch.id == data.branch_id)
        branch_result = await db.execute(branch_query)
        branch = branch_result.scalar_one_or_none()

        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch with ID {data.branch_id} not found"
            )

        menu = Menu(**data.dict(exclude_unset=True))
        db.add(menu)
        await db.commit()
        await db.refresh(menu)

        logger.info(f"Menu created successfully: {menu.id}")
        return menu

    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error creating menu: {str(e)}")

        error_msg = str(e).lower()
        if "unique constraint" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Menu with this name already exists for this branch"
            )
        elif "foreign key constraint" in error_msg:
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


async def get_menu(db: AsyncSession, menu_id: int) -> Menu:
    try:
        query = (
            select(Menu)
            .options(selectinload(Menu.branch))
            .where(Menu.id == menu_id)
        )
        result = await db.execute(query)
        menu = result.scalar_one_or_none()

        if not menu:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu with ID {menu_id} not found"
            )

        return menu

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving menu"
        )


async def get_menu_by_branch(db: AsyncSession, branch_id: int) -> List[Menu]:
    try:
        branch_query = select(Branch).where(Branch.id == branch_id)
        branch_result = await db.execute(branch_query)
        branch = branch_result.scalar_one_or_none()

        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch with ID {branch_id} not found"
            )

        query = (
            select(Menu)
            .options(selectinload(Menu.branch))
            .where(Menu.branch_id == branch_id)
            .order_by(Menu.created_at.desc())
        )
        result = await db.execute(query)
        menus = result.scalars().all()

        return list(menus)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching menus for branch {branch_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving menus"
        )


async def get_menus_paginated(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Menu]:
    try:
        query = (
            select(Menu)
            .options(selectinload(Menu.branch))
            .offset(skip)
            .limit(limit)
            .order_by(Menu.created_at.desc())
        )
        result = await db.execute(query)
        menus = result.scalars().all()

        return list(menus)

    except Exception as e:
        logger.error(f"Error fetching paginated menus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving menus"
        )


async def update_menu(db: AsyncSession, menu_id: int, data: MenuUpdate) -> Menu:
    try:
        menu = await get_menu(db, menu_id)

        if data.branch_id and data.branch_id != menu.branch_id:
            branch_query = select(Branch).where(Branch.id == data.branch_id)
            branch_result = await db.execute(branch_query)
            branch = branch_result.scalar_one_or_none()

            if not branch:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Branch with ID {data.branch_id} not found"
                )

        update_data = data.dict(exclude_unset=True)

        stmt = (
            update(Menu)
            .where(Menu.id == menu_id)
            .values(**update_data)
            .returning(Menu)
        )

        result = await db.execute(stmt)
        await db.commit()

        updated_menu = result.scalar_one()
        await db.refresh(updated_menu)

        logger.info(f"Menu {menu_id} updated successfully")
        return updated_menu

    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error updating menu {menu_id}: {str(e)}")

        error_msg = str(e).lower()
        if "unique constraint" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Menu with this name already exists for this branch"
            )
        elif "foreign key constraint" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid branch reference"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating menu due to data constraints"
            )

    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating menu"
        )


async def patch_menu(db: AsyncSession, menu_id: int, data: MenuPatch) -> Menu:
    try:
        menu = await get_menu(db, menu_id)

        update_data = data.dict(exclude_unset=True)

        if not update_data:
            logger.info(f"No fields to update for menu {menu_id}")
            return menu

        if 'branch_id' in update_data:
            branch_query = select(Branch).where(Branch.id == update_data['branch_id'])
            branch_result = await db.execute(branch_query)
            branch = branch_result.scalar_one_or_none()

        update_data['updated_at'] = datetime.utcnow()

        stmt = (
            update(Menu)
            .where(Menu.id == menu_id)
            .values(**update_data)
            .returning(Menu)
        )

        result = await db.execute(stmt)
        updated_menu = result.scalar_one_or_none()

        if not updated_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Menu with ID {menu_id} not found"
            )

        await db.commit()

        await db.refresh(updated_menu)

        logger.info(f"Menu {menu_id} patched successfully. Updated fields: {list(update_data.keys())}")
        return updated_menu

    except HTTPException:
        await db.rollback()
        raise

    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Integrity error patching menu {menu_id}: {str(e)}")

        error_msg = str(e).lower()

        if "unique constraint" in error_msg:
            if "name" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A menu with this name already exists for this branch"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Duplicate value detected. Please check your input data"
                )

        elif "foreign key constraint" in error_msg:
            if "branch_id" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The specified branch does not exist"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reference to related data"
                )

        elif "check constraint" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data validation failed. Please check field values and constraints"
            )

        else:
            logger.error(f"Unhandled integrity error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data integrity error. Please check your input and try again"
            )

    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error patching menu {menu_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the menu"
        )


async def delete_menu(db: AsyncSession, menu_id: int):
    try:
        menu = await get_menu(db, menu_id)

        if menu.is_active:
            menu.is_active = False
            await db.commit()
            await db.refresh(menu)

        return {"success": True}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting company {menu_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
