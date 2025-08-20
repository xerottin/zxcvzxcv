from datetime import datetime

from pydantic import BaseModel


class MenuItemCreate(BaseModel):
    username: str
    logo: str | None = None
    description: str | None = None
    price: int
    is_available: bool = True
    menu_id: int


class MenuItemResponse(BaseModel):
    id: int
    username: str
    logo: str | None = None
    description: str | None = None
    price: int
    is_available: bool
    menu_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MenuItemInDB(MenuItemResponse):
    pass


class MenuItemUpdate(BaseModel):
    username: str | None = None
    logo: str | None = None
    descriptiom: str | None = None
    price: int | None = None
    is_available: bool = True
