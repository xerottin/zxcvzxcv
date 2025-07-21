from typing import Optional

from pydantic import BaseModel


class CompanyBase(BaseModel):
    id: int
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    logo: Optional[str] = None
    address: Optional[str] = None
    user_id = int
    class Config:
        orm_mode = True

class CompanyCreate(CompanyBase):
    pass

class CompanyInDb(CompanyBase):
    pass
