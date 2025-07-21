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
