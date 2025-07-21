from typing import Optional

from pydantic import BaseModel


class BranchBase(BaseModel):
    username: str
    url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating: Optional[float] = None
    class Config:
        orm_mode = True

class BranchCreate(BranchBase):
    pass

class BranchInDb(BranchBase):
    pass
