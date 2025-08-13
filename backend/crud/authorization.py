import logging
import random
import re
import string
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from core.security import get_password_hash
from fastapi import HTTPException
from models import User
from models.authorization import VerificationCode
from models.user import UserRole
from schemas.user import UserRegister
from sqlalchemy import and_, delete, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def create_public_user(db: AsyncSession, data: UserRegister) -> User:
    try:
        conditions = []
        if data.email:
            conditions.append(User.email == data.email)
        if data.phone:
            conditions.append(User.phone == data.phone)

        if conditions:
            existing_user = await db.scalar(
                select(User).where(
                    or_(*conditions) & (User.is_active == True)
                )
            )
            if existing_user:
                if existing_user.email == data.email:
                    raise HTTPException(status_code=409, detail="Email already registered")
                if existing_user.phone == data.phone:
                    raise HTTPException(status_code=409, detail="Phone number already registered")

        if not data.username:
            if data.email:
                base = re.split(r"@+", data.email)[0]
                base = re.sub(r"\W+", "", base) or "user"
            elif data.phone:
                base = f"user{data.phone[-4:]}" if len(data.phone) >= 4 else "user"
            username = f"{base}_{uuid4().hex[:6]}"
        else:
            username = data.username

        existing_username = await db.scalar(
            select(User).where(User.username == username)
        )
        if existing_username:
            username = f"{username}_{uuid4().hex[:4]}"

        normalized_phone = None
        if data.phone:
            normalized_phone = re.sub(r'[\s\-\(\)]', '', data.phone)

        user = User(
            username=username,
            email=data.email,
            phone=normalized_phone,
            hashed_password=get_password_hash(data.password),
            role=UserRole.user
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Unexpected error in create_public_user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")



def generate_verification_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


async def generate_and_send_code(
        db: AsyncSession,
        email: Optional[str] = None,
        phone: Optional[str] = None
) -> str:
    try:
        conditions = []
        if email:
            conditions.append(VerificationCode.email == email)
        if phone:
            normalized_phone = re.sub(r'[\s\-\(\)]', '', phone)
            conditions.append(VerificationCode.phone == normalized_phone)

        if conditions:
            stmt = delete(VerificationCode).where(
                or_(*conditions) &
                (VerificationCode.is_used == False)
            )
            await db.execute(stmt)

        code = generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        normalized_phone = None
        if phone:
            normalized_phone = re.sub(r'[\s\-\(\)]', '', phone)

        verification_code = VerificationCode(
            email=email,
            phone=normalized_phone,
            code=code,
            expires_at=expires_at
        )

        db.add(verification_code)
        await db.commit()

        if email:
            await send_email_code(email, code)
        if phone:
            await send_sms_code(phone, code)

        return code

    except Exception as e:
        await db.rollback()
        logger.error(f"Error generating verification code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to send verification code")


async def verify_code(
        db: AsyncSession,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        code: str = None
) -> bool:
    try:
        conditions = [
            VerificationCode.code == code,
            VerificationCode.is_used == False,
            VerificationCode.expires_at > datetime.utcnow()
        ]

        if email:
            conditions.append(VerificationCode.email == email)
        if phone:
            normalized_phone = re.sub(r'[\s\-\(\)]', '', phone)
            conditions.append(VerificationCode.phone == normalized_phone)

        stmt = select(VerificationCode).where(and_(*conditions))
        result = await db.execute(stmt)
        verification_code = result.scalar_one_or_none()

        if not verification_code:
            return False

        verification_code.is_used = True
        verification_code.is_active = False
        await db.commit()

        return True

    except Exception as e:
        await db.rollback()
        logger.error(f"Error verifying code: {e}", exc_info=True)
        return False


async def send_email_code(email: str, code: str):
    logger.info(f"Sending email code {code} to {email}")
    # Integrate with email service here
    pass


async def send_sms_code(phone: str, code: str):
    logger.info(f"Sending SMS code {code} to {phone}")
    # Integrate with SMS service here
    pass
