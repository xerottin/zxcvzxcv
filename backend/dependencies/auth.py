import logging
from typing import Optional

from core.security import decode_access_token
from db.session import get_pg_db
from dependencies.permission import ASSIGN_RULES
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from models import User
from models.user import UserRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

logger = logging.getLogger(__name__)


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
            logger.warning("Token without 'sub' claim")
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError) as e:
        logger.warning(f"Token validation failed: {type(e).__name__}")
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        logger.warning(f"User not found: {user_id}")
        raise credentials_exception

    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user_id}")
        raise credentials_exception

    return user

async def get_by_username(db: AsyncSession, username: str):
    # result = await db.execute(select(User).where((User.username == username) & (User.is_active == True)))
    result = await db.execute(select(User).where(User.username == username, User.is_active == True))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


async def require_admin_or_company(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.admin, UserRole.company]:
        raise HTTPException(status_code=403, detail="Admin or Company access required")
    return current_user


async def require_company_or_branch(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.company, UserRole.branch]:
        raise HTTPException(status_code=403, detail="Company or Branch access required")
    return current_user

async def require_branch(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.branch:
        raise HTTPException(status_code=403, detail="Branch access required")
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
