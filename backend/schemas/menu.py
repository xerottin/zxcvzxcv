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
