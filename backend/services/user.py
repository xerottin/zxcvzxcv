#business logic
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.base import UserRole


async def update_user_role(
    db: AsyncSession,
    user_id: int,
    new_role: UserRole
) -> User:
    query = await db.execute(select(User).where(User.id == user_id))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == new_role:
        return user

    user.role = new_role
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
