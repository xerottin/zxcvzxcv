from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from core.settings import settings
from db.session import get_pg_db
from api import router as api_router

import logging
from contextlib import asynccontextmanager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    yield
    # Shutdown
    logger.info("Application shutting down...")

app = FastAPI(
    title="Coffee-Shop-API",
    description="Coffee Shop Management API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/ping")
async def ping(db: AsyncSession = Depends(get_pg_db)):
    await db.execute(text("SELECT 1"))
    return {"message": "pong"}

@app.get("/health", include_in_schema=False, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_pg_db)):
    try:
        result = await db.execute(text("SELECT version()"))
        db_version = result.scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "version": app.version,
            "environment": "production" if not settings.DEBUG else "development"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(503, {"detail": "Service unavailable", "database": "disconnected"})
