import asyncio

from app.database.database import async_engine
from app.database.models import Base
from loguru import logger


async def init_models():
    async with async_engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы созданы")


if __name__ == "__main__":
    asyncio.run(init_models())
