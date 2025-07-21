from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.company import create_company
from db.session import get_pg_db
from dependencies.auth import require_admin
from models import User
from schemas.company import CompanyCreate, CompanyInDb

router = APIRouter(prefix="", tags=["Companies"])


@router.post("/", response_model=CompanyInDb, status_code=status.HTTP_201_CREATED)
async def create_company_endpoint(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_pg_db),
    current_user: User = Depends(require_admin)
):
    return await create_company(db, data)
