import enum
from typing import List

from sqlalchemy import String, Boolean
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models.base import BaseModel

class UserRole(enum.Enum):
    admin = "admin"
    company = "company"
    branch = "branch"
    user = "user"

class User(BaseModel):
    __tablename__ = 'user'

    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role", create_type=True),
        nullable=False
    )

    branch: Mapped[["Branch"]] = relationship("Branch", back_populates="owner", uselist=False)
    company: Mapped[["Company"]] = relationship("Company", back_populates="owner", uselist=False)    
    order: Mapped[List["Order"]] = relationship("Order", back_populates="user")
    basket_item: Mapped[List["Basket"]] = relationship("Basket", back_populates="user", cascade="all, delete-orphan")