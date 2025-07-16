from typing import Optional

from pydantic import BaseModel, EmailStr

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
    password: str
    role: UserRole = UserRole.user


class UserUpdate(UserBase):
    role: UserRole = UserRole.user
    password: Optional[str] = None
    phone: Optional[str] = None
    is_verified: Optional[bool] = False

class UserRoleUpdate(UserBase):
    role: UserRole
