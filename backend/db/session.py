from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from core.settings import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
    future=True
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
