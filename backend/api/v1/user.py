from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserCreate, UserRead
from crud.user import create_user
from db.session import get_pg_db

router = APIRouter()


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_view(
    user: UserCreate,
    db: AsyncSession = Depends(get_pg_db)
):
    try:
        return await create_user(db, user)
    except HTTPException as e:
        raise e
