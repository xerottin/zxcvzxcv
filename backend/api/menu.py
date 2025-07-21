from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_pg_db
from dependencies.auth import require_branch
from models import User
from crud.menu import create_branch_menu
from models.branch import MenuItem
from schemas.menu import MenuBase

router = APIRouter(prefix="", tags=["Menus"])

@router.post("/create", response_model=MenuBase, status_code=status.HTTP_201_CREATED)
async def create_menu(
        data: MenuBase,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await create_branch_menu(db, data)

@router.post("/create/item", response_model=MenuItemBase, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
        data: MenuItemBase,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await create_menu_item(db, data)




