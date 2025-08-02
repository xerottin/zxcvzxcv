from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from db.session import get_pg_db
from dependencies.auth import get_current_user
from models.user import User
from schemas.basket import BasketResponse, BasketCreateSchema, BasketUpdateSchema, BasketListResponse
from crud.basket import (
    create_basket,
    get_basket,
    get_baskets,
    update_basket,
    update_patch_basket,
    delete_basket,
    clear_user_basket
)

router = APIRouter()


@router.post("/", response_model=BasketResponse, status_code=status.HTTP_201_CREATED)
async def create_basket_endpoint(
    user_id: int,
    payload: BasketCreateSchema,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    return await create_basket(db, payload, user_id)


@router.get("/", response_model=BasketListResponse)
async def list_baskets(
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return")
):
    return await get_baskets(db, current_user.id, skip, limit)


@router.get("/{basket_id}", response_model=BasketResponse)
async def get_basket_endpoint(
    basket_id: int,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    basket = await get_basket(db, basket_id)
    
    if basket.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    
    return basket


@router.put("/{basket_id}", response_model=BasketResponse)
async def update_basket_endpoint(
    basket_id: int,
    payload: BasketUpdateSchema,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    return await update_basket(db, basket_id, payload, current_user.id)


@router.patch("/{basket_id}", response_model=BasketResponse)
async def patch_basket_endpoint(
    basket_id: int,
    quantity: int,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    return await update_patch_basket(db, basket_id, quantity, current_user.id)


@router.delete("/{basket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_basket_endpoint(
    basket_id: int,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    await delete_basket(db, basket_id, current_user.id)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_basket_endpoint(
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user)
):
    await clear_user_basket(db, current_user.id)