from fastapi import HTTPException, status

from models import User
from models.base import UserRole

ASSIGN_RULES: dict[UserRole, set[UserRole]] = {
    UserRole.admin:     set(UserRole),
    UserRole.company:   {UserRole.cafeteria, UserRole.user},
    UserRole.cafeteria: {UserRole.user}, # need add stuff
}


def check_assign_permission(
    new_role: UserRole,
    current: User,
) -> None:
    allowed = ASSIGN_RULES.get(current.role, set())
    if new_role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot assign this role",
        )
