from typing import List

from crud.user import (
    create_user,
    delete_user,
    get_user,
    get_users,
    update_user,
    update_user_role,
)
from db.session import get_pg_db
from dependencies.auth import check_assign_permission, get_current_user, require_admin
from fastapi import APIRouter, Depends, Path, status
from models import User
from schemas.user import UserCreate, UserInDB, UserRoleUpdate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/create", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    payload: UserCreate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(require_admin),
):
    return await create_user(db, payload)


@router.get("/me", response_model=UserInDB)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/list_users", response_model=List[UserInDB])
async def list_users(
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    return await get_users(db)


@router.get("/get_user/{user_id}", response_model=UserInDB)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(require_admin),
):
    return await get_user(db, user_id)


@router.put("/update/{user_id}", response_model=UserInDB)
async def update_user_endpoint(
    user_id: int,
    user: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_pg_db),
):
    updated_user = await update_user(db, user_id, user)
    return UserInDB.from_orm(updated_user)


@router.patch(
    "/role/{user_id}",
    response_model=UserInDB,
    status_code=status.HTTP_200_OK,
)
async def patch_user_role(
    user_id: int = Path(..., ge=1),
    payload: UserRoleUpdate = Depends(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_pg_db),
):
    check_assign_permission(payload.role, current_user)
    return await update_user_role(db, user_id, payload.role)


@router.delete("/delete/{user_id}", status_code=204)
async def delete_user_endpoint(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_pg_db),
):
    await delete_user(db, user_id)
