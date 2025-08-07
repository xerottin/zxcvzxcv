from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, field_validator


class CleanupType(str, Enum):
    UNVERIFIED_USERS = "unverified_users"
    EXPIRED_CODES = "expired_codes"
    ALL = "all"


class CleanupRequest(BaseModel):
    cleanup_type: CleanupType = CleanupType.ALL
    days_threshold: int = 7
    dry_run: bool = False
    force: bool = False

    @field_validator('days_threshold')
    @classmethod
    def validate_days_threshold(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Days threshold must be at least 1')
        if v > 365:
            raise ValueError('Days threshold cannot exceed 365 days')
        return v


class CleanupResponse(BaseModel):
    status: str
    cleanup_type: CleanupType
    dry_run: bool
    deleted_users: int = 0
    deleted_codes: int = 0
    processed_users: List[dict] = []
    execution_time: float
    message: str
    timestamp: datetime


class CleanupStats(BaseModel):
    total_users: int
    verified_users: int
    unverified_users: int
    unverified_old_users: int
    total_verification_codes: int
    expired_codes: int
    active_codes: int
