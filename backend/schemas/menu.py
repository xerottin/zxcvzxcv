from typing import Optional

from models import BaseModel


class MenuBase(BaseModel):
    name: str
    logo: Optional[str] = None
    branch_id: Optional[int] = None

