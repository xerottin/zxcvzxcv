from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_pg_db
from core.security import verify_password, create_access_token
from models import User
from core.security import login_for_access_token
from schemas.token import Token

router = APIRouter(prefix="", tags=["auth"])

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_pg_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user: User | None = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login_token(
        form_data=Depends(),
        db: AsyncSession = Depends(get_pg_db)
):
    return await login_for_access_token(form_data, db)
