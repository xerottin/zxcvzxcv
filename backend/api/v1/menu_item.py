from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.menu_item import create_menu_item_crud
from db.session import get_pg_db
from dependencies.auth import require_branch
from models import User
from schemas.menu_item import MenuItemCreate, MenuItemResponse

router = APIRouter(prefix="", tags=["Menu-Item"])


@router.post("/create", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item_endpoint(
        data: MenuItemCreate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await create_menu_item_crud(db, data, current_user.id)

@router.get("{menu_item_id}", response_model=MenuResponse, status_code=status.HTTP_200_OK)
async def get_menu_item_endpoint(
        menu_item_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await get_menu(menu_item_id, db)

@router.put("{menu_item_id}", response_model=MenuResponse, status_code=status.HTTP_200_OK)
async def update_menu_item_endpoint(
        menu_item_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await put_menu(menu_item_id, db)

@router.patch("/{menu_item_id}", response_model=MenuResponse, status_code=status.HTTP_200_OK)
async def patch_menu_item_endpoint(
        menu_item_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await patch_menu(menu_item_id, db)

@router.delete("/{menu_item_id}")
async def delete_menu_item_endpoint(
        menu_item_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await delete_menu(menu_item_id, db)
