from sqlalchemy import Column, String, Boolean, Enum

from models.base import BaseModel, UserRole


class User(BaseModel):
    __tablename__ = 'user'

    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=True)
    is_verified = Column(Boolean, nullable=True, default=False)
    role = Column(Enum(UserRole, name="user_role"), default=UserRole.user, nullable=False)
