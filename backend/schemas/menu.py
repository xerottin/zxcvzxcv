# schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


# Menu schemas
class MenuBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Menu name")
    logo: Optional[str] = Field(None, description="Menu logo URL")
    branch_id: int = Field(..., description="Branch ID this menu belongs to")


class MenuCreate(MenuBase):
    pass


class MenuResponse(MenuBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True


# MenuItem schemas
class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Menu item name")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: Optional[Decimal] = Field(None, ge=0, description="Item price")
    logo: Optional[str] = Field(None, description="Item image URL")
    is_available: bool = Field(True, description="Item availability status")
    menu_id: int = Field(..., description="Menu ID this item belongs to")


class MenuItemCreate(MenuItemBase):
    pass


class MenuItemResponse(MenuItemBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

