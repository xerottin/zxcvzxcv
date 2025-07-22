from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from crud.menu import (
    create_menu, get_menu, get_menu_by_branch,
    update_menu, patch_menu, delete_menu, get_menus_paginated
)
from db.session import get_pg_db
from dependencies.auth import require_branch
from models import User
from schemas.menu import MenuResponse, MenuCreate, MenuUpdate, MenuPatch

router = APIRouter(prefix="", tags=["Menus"])


@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_endpoint(
        data: MenuCreate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await create_menu(db, data)


@router.get("/", response_model=List[MenuResponse])
async def get_menus_endpoint(
        branch_id: Optional[int] = Query(None, description="Filter by branch ID"),
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    if branch_id:
        return await get_menu_by_branch(db, branch_id)
    return await get_menus_paginated(db, skip=skip, limit=limit)


@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu_endpoint(
        menu_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await get_menu(db, menu_id)


@router.put("/{menu_id}", response_model=MenuResponse)
async def update_menu_endpoint(
        menu_id: int,
        data: MenuUpdate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await update_menu(db, menu_id, data)


@router.patch("/{menu_id}", response_model=MenuResponse)
async def patch_menu_endpoint(
        menu_id: int,
        data: MenuPatch,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    return await patch_menu(db, menu_id, data)


@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_endpoint(
        menu_id: int,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_branch)
):
    await delete_menu(db, menu_id)
    return None
