from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CompanyBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    logo: Optional[str] = None
    address: Optional[str] = None
    owner_id: Optional[int] = None
    class Config:
        orm_mode = True

class CompanyCreate(CompanyBase):
    pass

class CompanyInDb(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime
