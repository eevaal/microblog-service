from contextlib import asynccontextmanager

from sqlalchemy import engine
from microblog_service.database.database import engine, Base
from fastapi import FastAPI
from src.microblog_service.api.v1.posts import router as posts_router

from microblog_service.models.post import Post

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(posts_router, prefix="/api/v1", tags=["posts"])

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Microblog Service!"}

@app.get("/health")
async def check_health():
    return {"status": "healthy"}