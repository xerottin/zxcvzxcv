from typing import List

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user import get_users, get_user, update_user, delete_user, create_user
from dependencies.auth import get_current_user, check_assign_permission
from models import User
from schemas.user import UserCreate, UserRead, UserInDB, UserUpdate, UserRoleUpdate
from db.session import get_pg_db
from services.user import update_user_role

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    payload: UserCreate,
    db: AsyncSession = Depends(get_pg_db),
):
    return await create_user(db, payload)


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[UserInDB])
async def list_users(db: AsyncSession = Depends(get_pg_db)
                     # , current_user: User = Depends(get_current_user)
                     ):
    return await get_users(db)


@router.get("/", response_model=UserInDB)
async def get_user_endpoint(db: AsyncSession = Depends(get_pg_db), current_user: User = Depends(get_current_user)):
    return await get_user(db, current_user.id)


@router.put("/", response_model=UserInDB)
async def update_user_endpoint(
        user: UserUpdate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(get_current_user)
):
    updated_user = await update_user(db, current_user.id, user)
    return UserInDB.from_orm(updated_user)

@router.patch(
    "/{user_id}/role",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def patch_user_role(
    user_id: int = Path(..., ge=1),
    payload: UserRoleUpdate = Depends(),
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(get_current_user),
):
    check_assign_permission(payload.role, current_user)
    return await update_user_role(db, user_id, payload.role)


@router.delete("/{user_id}", status_code=204)
async def delete_user_endpoint(db: AsyncSession = Depends(get_pg_db), current_user: User = Depends(get_current_user)):
    await delete_user(db, current_user.id)
    return {"success" : True}
