from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional
import logging

from models.menu import Menu
from schemas.menu import MenuCreate, MenuResponse
from models.branch import Branch

logger = logging.getLogger(__name__)


async def create_branch_menu(db: AsyncSession, data: MenuCreate):
    try:
        branch_query = select(Branch).where(Branch.id == data.branch_id)
        branch_result = await db.execute(branch_query)
        branch = branch_result.scalar_one_or_none()

        if not branch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Branch with ID {data.branch_id} not found"
            )

        menu = Menu(**data.dict())

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
