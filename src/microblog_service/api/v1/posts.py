import json

from fastapi import APIRouter, Query, Request, status, Depends
import redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from redis import asyncio as aioredis

from microblog_service.database.database import get_db
from microblog_service.schemas.post import PostCreate, PostResponse
from microblog_service.models.post import Post

router = APIRouter()

def get_redis_client(request: Request) -> aioredis.Redis:
    return request.app.state.redis


@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis_client)
):
    
    cache_key = f"posts:limit={limit}:offset={offset}"
    cached_posts = await redis.get(cache_key)
    if cached_posts:
        return json.loads(cached_posts)

    query = select(Post).offset(offset).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()

    post_jsonable = [PostResponse.model_validate(posts).model_dump(mode="json") for posts in posts]

    await redis.set(
        cache_key,
        json.dumps(post_jsonable),
        ex=30
    )

    return posts


@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis_client)
):
    new_post = Post(**payload.model_dump())

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    cache_keys = await redis.keys("posts:*")
    for key in cache_keys:
        await redis.delete(key)
    
    return new_post