import logging
import re
from uuid import uuid4

from fastapi import HTTPException
from models import User
from models.user import UserRole
from schemas.user import UserCreate, UserUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.security import get_password_hash

logger = logging.getLogger(__name__)


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    try:
        existing_user = await db.scalar(
            select(User).where(
                (User.email == data.email) & (User.is_active == True)
            )
        )
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already registered")

        if not data.username:
            base = re.split(r"@+", data.email)[0]
            base = re.sub(r"\W+", "", base) or "user"
            username = f"{base}_{uuid4().hex[:6]}"
        else:
            username = data.username

        existing_username = await db.scalar(
            select(User).where(User.username == username)
        )
        if existing_username:
            username = f"{username}_{uuid4().hex[:4]}"

        user = User(
            username=username,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            role=data.role
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error in create_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).where(User.is_active == True).offset(skip).limit(limit))
    return result.scalars().all()


# Read one
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_by_username(db: AsyncSession, username: str):
    # result = await db.execute(select(User).where((User.username == username) & (User.is_active == True)))
    result = await db.execute(select(User).where(User.username == username, User.is_active == True))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    try:
        user = await get_user(db, user_id)

        protected_fields = {'id', 'created_at', 'hashed_password'}
        update_data = user_update.dict(exclude_unset=True)

        for key, value in update_data.items():
            if key not in protected_fields:
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)
        return user

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_active:
        user.is_active = False
        await db.commit()
        await db.refresh(user)

    return {"success": True, "message": "User deactivated"}


async def update_user_role(
        db: AsyncSession,
        user_id: int,
        new_role: UserRole
) -> User:
    query = await db.execute(select(User).where(User.id == user_id))
    user = query.scalar_one_or_none()
    if not user or user.is_active == False:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == new_role:
        return user

    user.role = new_role
    await db.commit()
    await db.refresh(user)
    return user
