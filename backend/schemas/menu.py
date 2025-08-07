from datetime import datetime

from pydantic import BaseModel


class MenuCreate(BaseModel):
    username: str
    logo: str | None = None
    logo: str | None = None
    description: str | None = None
    branch_id: int


class MenuInDB(BaseModel):
    id: int
    username: str
    logo: str | None = None
    description: str | None = None
    branch_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MenuResponse(BaseModel):
    id: int
    username: str
    logo: str | None = None
    description: str | None = None
    branch_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class MenuUpdate(BaseModel):
    username: str | None = None
    logo: str | None = None
    description: str | None = None
    branch_id: int | None = None


class MenuPatch(BaseModel):
    username: str | None = None
    logo: str | None = None
    description: str | None = None
    branch_id: int | None = None

    model_config = {
        "from_attributes": True
    }
