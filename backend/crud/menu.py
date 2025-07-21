from sqlite3 import IntegrityError

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.branch import Menu
from schemas.menu import MenuBase


async def create_branch_menu(db: AsyncSession, data: MenuBase) -> Menu:

    try:
        new_menu = Menu(
            name=data.name,
            logo=data.logo,
            branch_id=data.branch_id
        )

        db.add(new_menu)

        await db.commit()

        await db.refresh(new_menu)

        return new_menu

    except IntegrityError as e:
        await db.rollback()

        if "unique constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Menu already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating menu"
            )

    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

async def create_menu(db: AsyncSession, data: Menu) -> Menu:

