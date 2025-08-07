from datetime import datetime

from pydantic import BaseModel


class BranchBase(BaseModel):
    username: str
    url: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    rating: float | None = None

    company_id: int | None = None
    owner_id: int | None = None

    model_config = {
        "from_attributes": True
    }


class BranchCreate(BranchBase):
    pass


class BranchInDb(BranchBase):
    id: int
    created_at: datetime
    updated_at: datetime
