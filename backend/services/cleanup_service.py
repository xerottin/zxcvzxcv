import logging
from datetime import datetime, timedelta, timezone

from models.authorization import VerificationCode
from models.user import User
from schemas.tasks import CleanupRequest
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def _cleanup_unverified_users_api(db: AsyncSession, payload: CleanupRequest) -> dict:
    deleted_count = 0
    processed_users = []

    try:
        cutoff_date = datetime.now(timezone.utc) - \
            timedelta(days=payload.days_threshold)

        logger.info(
            f"Starting cleanup of users created before {cutoff_date} (dry_run: {payload.dry_run})")

        stmt = select(User).where(
            and_(
                User.is_verified == False,
                User.created_at < cutoff_date,
                User.is_active == True
            )
        )

        result = await db.execute(stmt)
        users_to_delete = result.scalars().all()

        logger.info(
            f"Found {len(users_to_delete)} unverified users to process")

        for user in users_to_delete:
            user_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "created_at": user.created_at.isoformat(),
                "days_old": (datetime.now(timezone.utc) - user.created_at).days
            }
            processed_users.append(user_info)

            if not payload.dry_run:
                logger.info(
                    f"Deleting unverified user: {user.id}, email: {user.email}")

                codes_stmt = delete(VerificationCode).where(
                    or_(
                        VerificationCode.email == user.email,
                        VerificationCode.phone == user.phone
                    )
                )
                await db.execute(codes_stmt)

                user.is_active = False
                user.updated_at = datetime.now(timezone.utc)

                deleted_count += 1

        if not payload.dry_run:
            await db.commit()

        return {
            "deleted_users": deleted_count,
            "deleted_codes": 0,
            "processed_users": processed_users
        }

    except Exception as e:
        if not payload.dry_run:
            await db.rollback()
        logger.error(f"Error during users cleanup: {e}", exc_info=True)
        raise


async def _cleanup_expired_codes_api(db: AsyncSession, payload: CleanupRequest) -> dict:
    deleted_count = 0

    try:
        if not payload.dry_run:
            stmt = delete(VerificationCode).where(
                VerificationCode.expires_at < datetime.now(timezone.utc)
            )
            result = await db.execute(stmt)
            deleted_count = result.rowcount
            await db.commit()
        else:
            stmt = select(func.count(VerificationCode.id)).where(
                VerificationCode.expires_at < datetime.now(timezone.utc)
            )
            result = await db.execute(stmt)
            deleted_count = result.scalar()

        return {
            "deleted_users": 0,
            "deleted_codes": deleted_count,
            "processed_users": []
        }

    except Exception as e:
        if not payload.dry_run:
            await db.rollback()
        logger.error(f"Error during codes cleanup: {e}", exc_info=True)
        raise
