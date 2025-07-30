
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status

from schemas.order import OrderCreate, OrderInDB, OrderUpdate
from dependencies.auth import get_current_user
from models.user import User
from db.session import get_pg_db


router = APIRouter()

@router.post("/create", response_model=OrderInDB, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
        payload: OrderCreate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(get_current_user)
):
    return await create_order(db, payload)

@router.get("/{order_id}", response_model=OrderInDB)
async def get_order_endpoint(
        order_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(get_current_user)
):
    return await get_order(db, order_id)

@router.put("/{order_id}", response_model=OrderInDB)
async def update_order_endpoint(
        order_id: int,
        order: OrderUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_pg_db),
):
    updated_order = await update_order(db, order_id, order)
    return OrderInDB.from_orm(updated_order)

