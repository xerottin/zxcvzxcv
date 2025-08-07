import re

from core.security import create_access_token
from db.session import get_pg_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User
from schemas.user import CodeSentResponse, LoginRequest, TokenResponse, UserInDB, UserRegister, VerifyCodeRequest
from services.authorization import create_public_user, generate_and_send_code, verify_code
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(
        payload: UserRegister,
        db: AsyncSession = Depends(get_pg_db)

):
    return await create_public_user(db, payload)


@router.post("/login", response_model=CodeSentResponse)
async def send_login_code(
        payload: LoginRequest,
        db: AsyncSession = Depends(get_pg_db)
):
    conditions = []
    if payload.email:
        conditions.append(User.email == payload.email)
    if payload.phone:
        normalized_phone = re.sub(r'[\s\-\(\)]', '', payload.phone)
        conditions.append(User.phone == normalized_phone)

    stmt = select(User).where(
        or_(*conditions) & (User.is_active == True)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await generate_and_send_code(db, payload.email, payload.phone)

    return CodeSentResponse(
        message="Verification code sent successfully",
        expires_in=60
    )


@router.post("/verify", response_model=TokenResponse)
async def verify_login_code(
        payload: VerifyCodeRequest,
        db: AsyncSession = Depends(get_pg_db)
):
    is_valid = await verify_code(db, payload.email, payload.phone, payload.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    conditions = []
    if payload.email:
        conditions.append(User.email == payload.email)
    if payload.phone:
        normalized_phone = re.sub(r'[\s\-\(\)]', '', payload.phone)
        conditions.append(User.phone == normalized_phone)

    stmt = select(User).where(
        or_(*conditions) & (User.is_active == True)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_verified = True

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserInDB.model_validate(user)
    )
