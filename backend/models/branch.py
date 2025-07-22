from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

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
