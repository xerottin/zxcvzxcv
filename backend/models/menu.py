from typing import List
from sqlalchemy import String, Integer, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models import BaseModel


class Menu(BaseModel):
    __tablename__ = "menu"

    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    logo: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey('branch.id'), nullable=False)
    
    branch: Mapped["Branch"] = relationship("Branch", back_populates="menu", uselist=False)
    item: Mapped[List["MenuItem"]] = relationship("MenuItem", back_populates="menu", cascade="all, delete-orphan") 

class MenuItem(BaseModel):
    __tablename__ = "menu_item"    

    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    logo: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    
    menu_id: Mapped[int] = mapped_column(Integer, ForeignKey('menu.id'), nullable=False)

    menu: Mapped["Menu"] = relationship("Menu", back_populates="item", uselist=False)
    order: Mapped["Order"] = relationship("Order", back_populates="menu_item")