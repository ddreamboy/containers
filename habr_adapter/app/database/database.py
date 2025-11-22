import asyncio
from typing import AsyncGenerator

from config import settings
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

async_engine = create_async_engine(
    url=settings.DB_URL,
    echo=settings.DEV_MODE,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

AsyncScopedSession = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=lambda: id(asyncio.current_task()),
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncScopedSession() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
