from typing import Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_pg_db
from dependencies.permission import CREATE_RULES
from models import User
from core.security import decode_access_token
from models.base import UserRole

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


def check_create_permission(
    new_role: UserRole,
    current: Optional[User] = Security(get_current_user, scopes=[]),
):
    if new_role == UserRole.user and current is None:
        return None

    if current is None:
        raise HTTPException(status_code=401, detail="Auth required")

    allowed = CREATE_RULES.get(current.role, set())
    if new_role not in allowed:
        raise HTTPException(status_code=403, detail="Forbidden to create this role")
    return current
