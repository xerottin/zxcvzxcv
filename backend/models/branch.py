from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models import BaseModel


class Branch(BaseModel):
    __tablename__ = "branches"
    username = Column(String, unique=True, nullable=False)
    phone = Column(String)
    url = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float)

    company_id = Column(Integer, ForeignKey('company.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))

    # Relationships
    owner = relationship("User", back_populates="branch")
    menus = relationship("Menu", back_populates="branch")  # Добавляем эту строку


class Menu(BaseModel):
    __tablename__ = "menus"
    name = Column(String, unique=True, nullable=False)
    logo = Column(String)

    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=False)
    branch = relationship("Branch", back_populates="menus")
    items = relationship("MenuItem", back_populates="menu", cascade="all, delete-orphan")


class MenuItem(BaseModel):
    __tablename__ = "menu_items"

    name = Column(String, nullable=False)
    logo = Column(String)
    description = Column(Text)
    price = Column(Numeric(10, 2))
    is_available = Column(Boolean, default=True)

    menu_id: Mapped[int] = mapped_column(Integer, ForeignKey('menus.id'), nullable=False)
    menu = relationship("Menu", back_populates="items")
