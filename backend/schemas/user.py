from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr

from models.base import UserRole


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
    password: str
    phone: Optional[str] = None
    is_verified: Optional[bool] = False
    role: UserRole

    class Config:
        orm_mode = True
        use_enum_values = True

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    phone: Optional[str] = None
    is_verified: Optional[bool] = False

