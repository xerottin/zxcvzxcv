
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_pg_db
from models import User
from dependencies.auth import get_current_user, check_assign_permission
from schemas.user import UserRead, UserRoleUpdate
from services.user import update_user_role

router = APIRouter()

@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }

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
    """
    Сменить роль пользователя.
    Тело: {"role": "cafeteria"}.
    Права проверяются через check_assign_permission.
    """
    return await update_user_role(db, user_id, payload.role)
