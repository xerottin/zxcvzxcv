from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Menu item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: Optional[Decimal] = Field(None, ge=0, description="Item price")
    logo: Optional[str] = Field(None, description="Item image URL")
    is_available: bool = Field(True, description="Item availability status")
    menu_id: int = Field(..., description="Menu ID this item belongs to")


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Menu item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: Optional[int]
    logo: Optional[str] = Field(None, description="Item image URL")
    is_available: Optional[bool] = Field(None, description="Item availability status")


class MenuItemResponse(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True
