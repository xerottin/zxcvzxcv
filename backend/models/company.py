from typing import List

from models import BaseModel
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Company(BaseModel):
    __tablename__ = "company"

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20))
    url: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    logo: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), unique=True)
    branch: Mapped[List["Branch"]] = relationship("Branch", back_populates="company")

    owner: Mapped["User"] = relationship("User", back_populates="company", uselist=False)
