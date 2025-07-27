from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, Field
from datetime import datetime

from models.user import UserRole

class UserBase(BaseModel):
    username: str | None = None


class UserCreate(UserBase):
    password: str
    email: EmailStr
    role: UserRole = UserRole.user

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        return v

class UserInDB(UserBase):
    id: int
    email: EmailStr
    phone = str | None = None
    is_verified: bool = False
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }

class UserResponse(UserBase):
    id: int
    email: EmailStr
    phone: str | None = None
    is_verified: bool = False
    role: UserRole
    created_at: datetime
    updated_at: datetime

class UserUpdate(UserBase):
    password: Optional[str] = None
    phone: Optional[str] = None
    is_verified: Optional[bool] = False

class UserRoleUpdate(UserBase):
    role: UserRole
