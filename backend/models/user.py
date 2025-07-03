from sqlalchemy import Column, String, Integer, Boolean

from models.base import BaseModel


class User(BaseModel):
    __tablename__ = 'user'
    username = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(Integer, unique=True, nullable=True)
    is_verified = Column(Boolean, nullable=True, default=False)
