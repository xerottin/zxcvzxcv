from datetime import datetime

from pydantic import BaseModel

class OrderCreate(BaseModel):
    user_id: int
    branch_id: int
    special_instructions: str | None = None
    delivery_address: str | None = None


class OrderResponse(BaseModel):
    id: int
    username: str
    user_id: int
    branch_id: int
    total_amount: int
    status: str
    created_at: datetime
    updated_at: datetime
    special_instructions: str | None = None
    delivery_address: str | None = None

    model_config = {
        "from_attributes": True
    }

class OrderInDB(OrderResponse):
    pass

class OrderUpdate(BaseModel):
    status: str
