from crud.menu_item import create_menu_item, get_menu_item, update_menu_item, patch_menu_item, delete_menu_item
from db.session import get_pg_db
from dependencies.auth import require_branch
from fastapi import APIRouter, Depends, status
from models import User
from schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="", tags=["Menu-Item"])


@router.post("/create", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item_endpoint(
        data: MenuItemCreate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await create_menu_item(db, data, current_user.id)


@router.get("/{menu_item_id}", response_model=MenuItemResponse, status_code=status.HTTP_200_OK)
async def get_menu_item_endpoint(
        menu_item_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await get_menu_item(db, menu_item_id)


@router.put("/{menu_item_id}", response_model=MenuItemResponse, status_code=status.HTTP_200_OK)
async def update_menu_item_endpoint(
        menu_item_id: int,
        data: MenuItemUpdate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await update_menu_item(db, menu_item_id, data, current_user.id)


@router.patch("/{menu_item_id}", response_model=MenuItemResponse, status_code=status.HTTP_200_OK)
async def patch_menu_item_endpoint(
        menu_item_id: int,
        data: MenuItemUpdate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await patch_menu_item(db, menu_item_id, data, current_user.id)


@router.delete("/{menu_item_id}", status_code=status.HTTP_200_OK)
async def delete_menu_item_endpoint(
        menu_item_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await delete_menu_item(db, menu_item_id, current_user.id)
