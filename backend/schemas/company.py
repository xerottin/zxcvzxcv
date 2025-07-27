from datetime import datetime

from pydantic import BaseModel

class CompanyCreate(BaseModel):
    username: str
    phone: str | None = None
    url: str | None = None
    email: str | None = None
    logo: str | None = None
    address: str | None = None
    owner_id: int

class CompanyInDB(BaseModel):
    id: int
    username: str
    phone: str | None = None
    url: str | None = None
    email: str | None = None
    logo: str | None = None
    address: str | None = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class CompanyUpdate(BaseModel):
    username: str | None = None
    phone: str | None = None
    url: str | None = None
    email: str | None = None
    logo: str | None = None
    address: str | None = None


