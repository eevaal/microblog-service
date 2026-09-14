from collections.abc import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from microblog_service.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL.unicode_string())
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

class Base(DeclarativeBase):
    pass