from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MenuItemCreate(BaseModel):
    username: str
    logo: str | None = None
    description: str | None = None
    price: float
    is_available: bool = True
    menu_id: int

class MenuItemResponse(BaseModel):
    id: int
    username: str
    logo: str | None = None
    description: str | None = None
    price: float
    is_available: bool
    menu_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
class MenuItemInDB(MenuItemResponse):
    pass

class MenuItemUpdate(BaseModel):
    username: str | None = None
    logo: str | None = None
    descriptiom: str | None = None
    price: float | None = None
    is_available: bool | None = None
