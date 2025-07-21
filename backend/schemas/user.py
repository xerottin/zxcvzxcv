from typing import Optional

from pydantic import BaseModel, EmailStr, validator, Field

from models.user import UserRole


class UserBase(BaseModel):
    username: Optional[str] = None


class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserInDB(UserBase):
    email: EmailStr
    phone: Optional[str] = None
    is_verified: Optional[bool] = False
    role: UserRole = UserRole.user

    class Config:
        orm_mode = True
        use_enum_values = True


class UserCreate(UserBase):

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.user
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        return v

class UserUpdate(UserBase):
    password: Optional[str] = None
    phone: Optional[str] = None
    is_verified: Optional[bool] = False

class UserRoleUpdate(UserBase):
    role: UserRole
