import logging
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Company, User
from schemas.company import CompanyCreate

logger = logging.getLogger(__name__)


async def create_company(db: AsyncSession, data: CompanyCreate) -> Company:
    try:
        if await db.scalar(select(Company).where(Company.name == data.name, Company.is_active)):
            raise HTTPException(status_code=409, detail="Company already exists")

        company = Company(**data.dict())
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating company: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_company(db: AsyncSession, company_id: int) -> Company:
    result = await db.execute(select(Company).where(Company.id == company_id, Company.is_active))
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


async def update_company_owner(db: AsyncSession, company_id: int, owner_id: int) -> Company:
    try:
        company = await get_company(db, company_id)

        owner = await db.scalar(select(User).where(User.id == owner_id, User.is_active == True))
        if not owner:
            raise HTTPException(status_code=400, detail="Owner user not found or inactive")

        if company.owner_id == owner_id:
            return company

        company.owner_id = owner_id
        await db.commit()
        await db.refresh(company)
        return company

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating company owner {company_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_company(db: AsyncSession, company_id: int):
    try:
        company = await get_company(db, company_id)

        if company.is_active:
            company.is_active = False
            await db.commit()
            await db.refresh(company)

        return {"success": True, "message": "Company deactivated"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting company {company_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_companies(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Company).where(Company.is_active == True).offset(skip).limit(limit)
    )
    return result.scalars().all()
