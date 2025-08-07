import re

from typing import Optional, Self

from pydantic import BaseModel, EmailStr, field_validator, model_validator
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
        if len(v) < 2:
            raise ValueError('Password too short')
        return v

class UserInDB(UserBase):
    id: int
    email: EmailStr
    phone: str | None = None
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
    passwrod: str | None = None
    phone: str | None = None
    is_verified: bool = False

class UserRoleUpdate(UserBase):
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str

    def model_post_init(self, __context):
        if not self.email and not self.phone:
            raise ValueError('Either email or phone must be provided')

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInDB

class UserRegister(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str
    username: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError('Password too short')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        phone_pattern = r'^\+?[\d\s\-\(\)]{10,15}$'
        if not re.match(phone_pattern, v.replace(' ', '').replace('-', '')):
            raise ValueError('Invalid phone number format')
        return v

    @model_validator(mode='after')
    def validate_contact_info(self) -> Self:
        if not self.email and not self.phone:
            raise ValueError('Either email or phone must be provided')
        return self

class VerifyCodeRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    code: str

    @model_validator(mode='after')
    def validate_contact_info(self) -> Self:
        if not self.email and not self.phone:
            raise ValueError('Either email or phone must be provided')
        return self

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInDB"

class CodeSentResponse(BaseModel):
    message: str
    expires_in: int 