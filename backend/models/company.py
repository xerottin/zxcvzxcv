from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from models.base import BaseModel


class Company(BaseModel):
    __tablename__ = "company"
    name = Column(String, unique=True, nullable=False)
    phone = Column(String)
    email = Column(String, unique=True)
    logo = Column(String)
    address = Column(String)

    owner = relationship("User", back_populates="company")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

