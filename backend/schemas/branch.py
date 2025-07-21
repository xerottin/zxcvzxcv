from typing import Optional

from pydantic import BaseModel


class BranchBase(BaseModel):
    id: int
    username: str
    url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    user_id: int
    class Config:
        orm_mode = True

class BranchCreate(BranchBase):
    pass
