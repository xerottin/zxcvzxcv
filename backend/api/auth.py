from core.security import create_access_token, login_for_access_token, verify_password
from db.session import get_pg_db
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from schemas.token import Token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_pg_db)
):
    result = await db.execute(select(User).where(User.email == form.username))
    user: User | None = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_token(form_data=Depends(), db: AsyncSession = Depends(get_pg_db)):
    return await login_for_access_token(form_data, db)
