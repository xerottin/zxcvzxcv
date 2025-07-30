from typing import List
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models import BaseModel


class Branch(BaseModel):
    __tablename__ = "branch"

    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(15))
    url: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    rating: Mapped[float] = mapped_column(Float)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey('company.id'))
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))

    company: Mapped["Company"] = relationship("Company", back_populates="branch")
    owner: Mapped["User"] = relationship("User", back_populates="branch", uselist=False)
    menu: Mapped["Menu"] = relationship("Menu", back_populates="branch")
    order: Mapped["Order"] = relationship("Order", back_populates="branch")