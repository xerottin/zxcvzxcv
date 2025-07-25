from datetime import datetime

from models.base import BaseModel


class OrderCreate(BaseModel):
    menu_item_id: int
    quantity: int = 1
    special_instructions: str = None
    delivery_address: str = None


class OrderResponse(BaseModel):
    id: int
    user_id: int
    menu_item_id: int
    quantity: int
    price: float
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    special_instructions: str = None
    delivery_address: str = None

    model_config = {
        "from_attributes": True
    }
