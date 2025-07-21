from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.branch import create_branch, update_owner_role_branch
from db.session import get_pg_db
from dependencies.auth import require_admin_or_company
from models import User
from schemas.branch import BranchInDb, BranchCreate
from schemas.company import CompanyCreate, CompanyInDb

router = APIRouter(prefix="", tags=["Branches"])


@router.post("/", response_model=BranchInDb, status_code=status.HTTP_201_CREATED)
async def create_branch_endpoint(
        data: BranchCreate,
        db: AsyncSession = Depends(get_pg_db),
        current_user: User = Depends(require_admin_or_company)
):
    return await create_branch(db, data)


@router.patch("/{branch_id}", response_model=BranchInDb, status_code=status.HTTP_200_OK)
async def add_owner_branch(
        branch_id: int,
        owner_id: int,
        current_user: User = Depends(require_admin_or_company),
        db: AsyncSession = Depends(get_pg_db)
):
    return await update_owner_role_branch(branch_id, owner_id, db)
