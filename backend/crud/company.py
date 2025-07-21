from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Company
from schemas.company import CompanyCreate


async def create_company(db: AsyncSession, data: CompanyCreate) -> Company:
    if await db.scalar(select(Company).where(Company.name == data.name)):
        raise HTTPException(status_code=403, detail="Company already exists")

    company = Company(**data.dict())
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company

async def update_owner_role( company_id: int, owner_id: int, db: AsyncSession):
    query = await db.execute(select(Company).where(Company.id == company_id))
    company = query.scalar_one_or_none()
    if not company or company.is_active == False:
        raise HTTPException(status_code=403, detail="Company does not exist")

    if company.owner_id == owner_id:
        return company

    company.owner_id = owner_id

    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company

