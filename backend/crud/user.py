import re
import logging
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from models import User
from models.user import UserRole
from schemas.user import UserCreate, UserUpdate
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
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except HTTPException as http_exc:
        await db.rollback()
        raise http_exc

    except ValueError as val_err:
        await db.rollback()
        logger.error(f"Validation error in create_user: {val_err}")
        raise HTTPException(status_code=400, detail=str(val_err))

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
    result = await db.execute(select(User).where(User.username == username) & (User.is_active == True))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    user = await get_user(db, user_id)
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int):
    user = await get_user(db, user_id)
    if user.is_active == True:
        user.is_active = False
        await db.commit()
        await db.refresh(user)
        return {"ok": True}
    else:
        return {"user not found": False}


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
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
