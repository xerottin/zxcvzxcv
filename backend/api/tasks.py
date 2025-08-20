import logging
from datetime import datetime, timedelta, timezone

from db.session import get_pg_db
from dependencies.auth import require_admin
from fastapi import APIRouter, Depends, HTTPException
from models.authorization import VerificationCode
from models.user import User
from schemas.tasks import CleanupRequest, CleanupResponse, CleanupStats, CleanupType
from services.cleanup_service import _cleanup_expired_codes_api, _cleanup_unverified_users_api
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.log import timeit

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/stats", response_model=CleanupStats)
async def get_cleanup_stats(
    days_threshold: int = 7,
    db: AsyncSession = Depends(get_pg_db),
    # current_user: User = Depends(require_admin)
):
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)

        total_users_stmt = select(func.count(User.id)).where(User.is_active == True)
        verified_users_stmt = select(func.count(User.id)).where(and_(User.is_active == True, User.is_verified == True))
        unverified_users_stmt = select(func.count(User.id)).where(
            and_(User.is_active == True, User.is_verified == False)
        )
        unverified_old_stmt = select(func.count(User.id)).where(
            and_(User.is_active == True, User.is_verified == False, User.created_at < cutoff_date)
        )

        total_codes_stmt = select(func.count(VerificationCode.id))
        expired_codes_stmt = select(func.count(VerificationCode.id)).where(
            VerificationCode.expires_at < datetime.now(timezone.utc)
        )
        active_codes_stmt = select(func.count(VerificationCode.id)).where(
            and_(VerificationCode.expires_at >= datetime.now(timezone.utc), VerificationCode.is_used == False)
        )

        results = await db.execute(
            select(
                total_users_stmt.scalar_subquery().label("total_users"),
                verified_users_stmt.scalar_subquery().label("verified_users"),
                unverified_users_stmt.scalar_subquery().label("unverified_users"),
                unverified_old_stmt.scalar_subquery().label("unverified_old_users"),
                total_codes_stmt.scalar_subquery().label("total_codes"),
                expired_codes_stmt.scalar_subquery().label("expired_codes"),
                active_codes_stmt.scalar_subquery().label("active_codes"),
            )
        )

        stats = results.first()

        return CleanupStats(
            total_users=stats.total_users,
            verified_users=stats.verified_users,
            unverified_users=stats.unverified_users,
            unverified_old_users=stats.unverified_old_users,
            total_verification_codes=stats.total_codes,
            expired_codes=stats.expired_codes,
            active_codes=stats.active_codes,
        )

    except Exception as e:
        logger.error(f"Error getting cleanup stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get cleanup statistics")


@router.post("/execute", response_model=CleanupResponse, include_in_schema=True)
async def execute_cleanup(
    payload: CleanupRequest,
    db: AsyncSession = Depends(get_pg_db),
    # current_user: User = Depends(require_admin)
):
    start_time = datetime.now(timezone.utc)

    try:
        if payload.cleanup_type == CleanupType.UNVERIFIED_USERS:
            result = await _cleanup_unverified_users_api(db, payload)
        elif payload.cleanup_type == CleanupType.EXPIRED_CODES:
            result = await _cleanup_expired_codes_api(db, payload)
        elif payload.cleanup_type == CleanupType.ALL:
            users_result = await _cleanup_unverified_users_api(db, payload)
            codes_result = await _cleanup_expired_codes_api(db, payload)
            result = {
                "deleted_users": users_result["deleted_users"],
                "deleted_codes": codes_result["deleted_codes"],
                "processed_users": users_result["processed_users"],
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid cleanup type")

        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()

        action = "Would delete" if payload.dry_run else "Deleted"
        message = f"{action} {result['deleted_users']} users and {result['deleted_codes']} codes"

        logger.info(
            # f"Cleanup executed by admin {current_user.username}: "
            f"{message} in {execution_time:.2f}s"
        )

        return CleanupResponse(
            status="success",
            cleanup_type=payload.cleanup_type,
            dry_run=payload.dry_run,
            deleted_users=result["deleted_users"],
            deleted_codes=result["deleted_codes"],
            processed_users=result["processed_users"],
            execution_time=execution_time,
            message=message,
            timestamp=end_time,
        )

    except Exception as e:
        logger.error(f"Cleanup execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Cleanup execution failed")
