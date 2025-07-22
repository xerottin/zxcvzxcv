from sqlalchemy import Column, String, Integer, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models import BaseModel


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
    price = Column(Integer)
    is_available = Column(Boolean, default=True)

    menu_id: Mapped[int] = mapped_column(Integer, ForeignKey('menus.id'), nullable=False)
    menu = relationship("Menu", back_populates="items")
