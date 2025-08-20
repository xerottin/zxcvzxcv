from typing import Optional

from crud.order import create_order, delete_order, get_order, get_orders, update_order
from db.session import get_pg_db
from dependencies.auth import get_current_user
from fastapi import APIRouter, Body, Depends, Path, Query, status
from models.order import OrderStatus
from models.user import User
from schemas.order import OrderCreate, OrderResponse, OrdersResponse, OrderUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/create", response_model=OrderResponse, status_code=status.HTTP_201_CREATED
)
async def create_order_endpoint(
    payload: OrderCreate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await create_order(db, payload)


@router.get("/", response_model=OrdersResponse)
async def get_orders_endpoint(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of orders to return"),
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await get_orders(db, user_id, branch_id, skip, limit)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await get_order(db, order_id, current_user.id)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_endpoint(
    order_id: int = Path(..., gt=0),
    payload: OrderUpdate = Body(...),
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await update_order(db, order_id, payload, current_user.id)


@router.delete("/{order_id}")
async def delete_order_endpoint(
    order_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await delete_order(db, order_id, current_user.id)
