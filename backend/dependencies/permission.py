from fastapi import HTTPException, status

from models import User
from models.user import UserRole

ASSIGN_RULES: dict[UserRole, set[UserRole]] = {
    UserRole.admin:     set(UserRole),
    UserRole.company:   {UserRole.branche, UserRole.user},
    UserRole.branche: {UserRole.user},
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


