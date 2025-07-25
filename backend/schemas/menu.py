from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


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
    model_config = {
        "from_attributes": True
    }


class MenuUpdate(MenuBase):
    is_active: bool = True

    model_config = {
        "from_attributes": True
    }



class MenuPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Menu name")
    logo: Optional[str] = Field(None, description="Menu logo URL")
    branch_id: Optional[int] = Field(None, gt=0, description="Branch ID this menu belongs to")
    is_active: Optional[bool] = None

    model_config = {
        "from_attributes": True
    }
