from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from db.session import get_pg_db

app = FastAPI()

@app.get("/ping")
async def ping(db: AsyncSession = Depends(get_pg_db)):
    await db.execute(text("SELECT 1"))
    return {"message": "pong"}
