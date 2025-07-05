from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from models import User
from models.base import UserRole
from schemas.user import UserCreate, UserUpdate
from utils.security import get_password_hash

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=UserRole.user,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).where(is_active=True).offset(skip).limit(limit))
    return result.scalars().all()

# Read one
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id, is_active=True))
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
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return {"ok": True}
