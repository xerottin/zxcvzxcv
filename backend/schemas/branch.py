from typing import Optional

from pydantic import BaseModel, ConfigDict


class BranchBase(BaseModel):
    username: str
    url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None

    model_config = {
        "from_attributes": True
    }

class BranchCreate(BranchBase):
    pass

class BranchInDb(BranchBase):
    id: int
