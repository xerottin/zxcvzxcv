import enum

from sqlalchemy import Column, String, Boolean
from sqlalchemy import Enum as SAEnum

from models.base import BaseModel

class UserRole(enum.Enum):
    __tablename__ = 'user_roles'

    admin = "admin"
    company = "company"
    branche = "branche"
    user = "user"

class User(BaseModel):
    __tablename__ = 'users'

    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    is_verified = Column(Boolean, nullable=True, default=False)
    role = Column(SAEnum(UserRole, name="user_role", create_type=True), default=UserRole.user)
