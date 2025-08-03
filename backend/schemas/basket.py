from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional

class MenuItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    logo: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    is_available: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BasketCreateSchema(BaseModel):
    menu_item_id: int = Field(..., gt=0, description="Menu item ID")
    quantity: int = Field(default=1, gt=0, le=99, description="Quantity of items")


class BasketUpdateSchema(BaseModel):
    menu_item_id: int = Field(..., gt=0, description="Menu item ID")
    quantity: int = Field(..., gt=0, le=99, description="Quantity of items")


class BasketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    menu_item_id: int
    quantity: int
    created_at: datetime
    updated_at: datetime
    menu_item: MenuItemResponse = None


class BasketListResponse(BaseModel):
    baskets: List[BasketResponse]
    total_count: int = Field(description="Total cost of all items in basket")