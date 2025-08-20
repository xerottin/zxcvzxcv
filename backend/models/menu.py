from typing import List

from models import BaseModel
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Menu(BaseModel):
    __tablename__ = "menu"

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    logo: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    branch_id: Mapped[int] = mapped_column(Integer, ForeignKey("branch.id"), nullable=False)

    branch: Mapped["Branch"] = relationship("Branch", back_populates="menu", uselist=False)
    menu_item: Mapped[List["MenuItem"]] = relationship("MenuItem", back_populates="menu", cascade="all, delete-orphan")


class MenuItem(BaseModel):
    __tablename__ = "menu_item"

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    logo: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    menu_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu.id"), nullable=False)

    menu: Mapped["Menu"] = relationship("Menu", back_populates="menu_item", uselist=False)
    basket: Mapped["Basket"] = relationship("Basket", back_populates="menu_item", cascade="all, delete-orphan")
    order_item: Mapped["OrderItem"] = relationship(
        "OrderItem", back_populates="menu_item", cascade="all, delete-orphan"
    )
