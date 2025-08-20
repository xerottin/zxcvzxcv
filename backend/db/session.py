from core.settings import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    settings.database_url, echo=True, pool_pre_ping=True, future=True
)

async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_pg_db():
    async with async_session() as session:
        yield session
