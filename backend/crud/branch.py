from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Branch
from schemas.branch import BranchCreate


async def create_branch(db: AsyncSession, data: BranchCreate) -> Branch:
    if await db.scalar(select(Branch).where(Branch.username == data.username)):
        raise HTTPException(status_code=400, detail="Branch already exists")

    branch = Branch(**data.dict())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch

async def update_owner_role_branch( branch_id: int, owner_id: int, db: AsyncSession):
    query = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = query.scalar_one_or_none()
    if not branch or branch.is_active == False:
        raise HTTPException(status_code=403, detail="Branch does not exist")

    if branch.owner_id == owner_id:
        return branch

    branch.owner_id = owner_id

    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch
