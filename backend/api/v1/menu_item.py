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
