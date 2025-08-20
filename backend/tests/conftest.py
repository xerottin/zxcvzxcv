import contextlib
import importlib
import os
import pkgutil
import sys

import httpx
import pytest_asyncio
from db.base import Base
from dependencies.auth import require_admin
from httpx import ASGITransport
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


def _import_all_models():
    try:
        pkg = importlib.import_module("models")
        for _, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
            if not ispkg:
                importlib.import_module(f"models.{modname}")
    except Exception:
        pass


TEST_DATABASE_URL = "sqlite+aiosqlite:///file::memory:?cache=shared"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"uri": True},
    poolclass=NullPool,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _prepare_database():
    _import_all_models()
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session():
    async with engine.connect() as conn:
        trans = await conn.begin()

        async_session_maker = async_sessionmaker(
            bind=conn, expire_on_commit=False, class_=AsyncSession, autoflush=False
        )
        async with async_session_maker() as session:
            nested = await session.begin_nested()

            @event.listens_for(session.sync_session, "after_transaction_end")
            def _restart_savepoint(sess, trans_):
                if trans_.nested and not trans_._parent.nested:
                    sess.begin_nested()

            try:
                yield session
            finally:
                with contextlib.suppress(Exception):
                    await nested.rollback()
                with contextlib.suppress(Exception):
                    await trans.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def _override_get_pg_db():
        yield db_session

    from main import app, get_pg_db

    app.dependency_overrides[get_pg_db] = _override_get_pg_db

    if require_admin is not None:

        class _DummyAdmin:
            id = 1
            username = "admin"
            role = "admin"
            is_active = True

        app.dependency_overrides[require_admin] = lambda: _DummyAdmin()

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
