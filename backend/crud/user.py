import re
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from models import User
from schemas.user import UserCreate, UserUpdate
from utils.security import get_password_hash

async def create_user(db: AsyncSession, data: UserCreate) -> User:
    if await db.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(status_code=409, detail="Email already registered")

    if not data.username:
        base = re.split(r"@+", data.email)[0]
        base = re.sub(r"\W+", "", base) or "user"
        username = f"{base}_{uuid4().hex[:6]}"
    else:
        username = data.username

    exists = await db.scalar(select(User).where(User.username == username))
    if exists:
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

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).where(is_active=True).offset(skip).limit(limit))
    return result.scalars().all()

# Read one
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id, User.is_active==True))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username, User.is_active==True))
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
