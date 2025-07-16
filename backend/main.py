from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from core.settings import settings
from db.session import get_pg_db
from api import router as api_router

app = FastAPI(
    title="Coffe-Shop-API",
    description="Coffe-Shop API",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    print("App started!")

@app.on_event("shutdown")
async def shutdown_event():
    print("App shutdown!")


@app.get("/ping")
async def ping(db: AsyncSession = Depends(get_pg_db)):
    await db.execute(text("SELECT 1"))
    return {"message": "pong"}

@app.get("/ping_pong", summary="Healthcheck", tags=["Service"])
async def ping():
    return {"status": "ok"}
