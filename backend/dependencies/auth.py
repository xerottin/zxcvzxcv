from typing import Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_pg_db
from dependencies.permission import ASSIGN_RULES
from models import User
from core.security import decode_access_token
from models.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_pg_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


async def require_admin_or_company(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.admin, UserRole.company]:
        raise HTTPException(status_code=403, detail="Admin or Company access required")
    return current_user


def check_assign_permission(
        target_role: UserRole,
        current: Optional[User] = Security(get_current_user, scopes=[]),
):
    if current is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    allowed = ASSIGN_RULES.get(current.role, set())
    if target_role not in allowed:
        raise HTTPException(status_code=403, detail="You cannot assign this role")
    return current
