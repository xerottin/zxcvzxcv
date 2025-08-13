import os
import sys
import importlib
import pkgutil

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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


