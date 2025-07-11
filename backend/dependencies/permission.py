from models.base import UserRole

CREATE_RULES: dict[UserRole, set[UserRole]] = {
    UserRole.admin:    {r for r in UserRole},
    UserRole.company:  {UserRole.cafeteria, UserRole.user},
    UserRole.cafeteria:{UserRole.user},
}
