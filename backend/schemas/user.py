from typing import Optional

from pydantic import BaseModel, EmailStr

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

class UserCreate(UserBase):
    email: EmailStr
    password: str
