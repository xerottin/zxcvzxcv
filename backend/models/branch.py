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
    owner = relationship("User", back_populates="branch")

    company_id = Column(Integer, ForeignKey('company.id'))
    owner_id = Column(Integer, ForeignKey('users.id'))

class Menu(BaseModel):
    __tablename__ = "menus"
    name = Column(String, unique=True, nullable=False)
    logo = Column(String)
    branch = relationship("Branch", back_populates="menus")

    branch_id = Column(Integer, ForeignKey('branches.id'))

class MenuItem(BaseModel):
    __tablename__ = "menu_items"
    name = Column(String, unique=True, nullable=False)
    logo = Column(String)
    menu = relationship("Menu", back_populates="menus")

    menu_id = Column(Integer, ForeignKey('menus.id'))

