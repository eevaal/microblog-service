from fastapi import APIRouter, Query, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from microblog_service.database.database import get_db
from microblog_service.schemas.post import PostCreate, PostResponse
from microblog_service.models.post import Post

router = APIRouter()

@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    query = select(Post).offset(offset).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()

    return posts


@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreate, db: AsyncSession = Depends(get_db)):
    new_post = Post(**payload.model_dump())

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post