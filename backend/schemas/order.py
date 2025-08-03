from datetime import datetime

from pydantic import BaseModel, ConfigDict

from models.order import OrderStatus
from schemas.basket import MenuItemResponse


class OrderCreate(BaseModel):
    user_id: int
    branch_id: int
    special_instructions: str | None = None
    delivery_address: str | None = None


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    quantity: int
    price: int
    total_price: int
    is_active: bool
    menu_item: MenuItemResponse


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    user_id: int
    branch_id: int
    total_amount: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    special_instructions: str | None = None
    delivery_address: str | None = None
    order_items: list[OrderItemResponse] = []


class OrderUpdate(BaseModel):
    status: OrderStatus = OrderStatus.PENDING
    special_instructions: str | None = None
    delivery_address: str | None = None


class OrdersResponse(BaseModel):
    orders: list[OrderResponse]
    total_count: int
    skip: int
    limit: int
