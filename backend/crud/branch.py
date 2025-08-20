import logging

from fastapi import HTTPException
from models import Branch
from schemas.branch import BranchCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def create_branch(db: AsyncSession, data: BranchCreate) -> Branch:
    try:
        if await db.scalar(select(Branch).where(Branch.username == data.username, Branch.is_active)):
            raise HTTPException(status_code=409, detail="Branch already exists")

        branch = Branch(**data.dict(exclude_unset=True))
        db.add(branch)
        await db.commit()
        await db.refresh(branch)
        return branch
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating branch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_branch(branch_id: int, db: AsyncSession):
    result = await db.execute(select(Branch).where(Branch.id == branch_id, Branch.is_active))
    branch = result.scalars().first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch does not exist")
    return branch


async def update_owner_role_branch(branch_id: int, owner_id: int, db: AsyncSession):
    try:
        query = await db.execute(select(Branch).where(Branch.id == branch_id))
        branch = query.scalar_one_or_none()
        if not branch or branch.is_active == False:
            raise HTTPException(status_code=404, detail="Branch does not exist")

        if branch.owner_id == owner_id:
            return branch

        branch.owner_id = owner_id

        await db.commit()
        await db.refresh(branch)
        return branch
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating branch owner {branch_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_branch(branch_id: int, db: AsyncSession):
    try:
        branch = await get_branch(branch_id, db)
        if branch.is_active:
            branch.is_active = False
            await db.commit()
            await db.refresh(branch)
            return {"ok": True}
        else:
            return {"branch not found": False}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting company {branch_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
