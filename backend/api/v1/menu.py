# routes.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.menu import create_branch_menu, create_menu_item_crud
from db.session import get_pg_db
from dependencies.auth import require_branch
from models import User
from schemas.menu import MenuResponse, MenuCreate, MenuItemResponse, MenuItemCreate

router = APIRouter(prefix="", tags=["Menus"])

@router.post("/create", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_endpoint(
    data: MenuCreate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(require_branch)
):
    return await create_branch_menu(db, data)

@router.post("/create/item", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item_endpoint(
    data: MenuItemCreate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(require_branch)
):

    return await create_menu_item_crud(db, data, current_user.id)
