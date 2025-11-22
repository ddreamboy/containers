import importlib
import json
from typing import Any, AsyncGenerator, Optional

from app.article_parser.parser import HabrParser
from app.article_parser.schemas import SArticleParsed, SParseRequest
from app.database.database import get_async_session
from app.database.models import Article
from config import settings
from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/habr", tags=["habr"])


async def get_parser():
    parser = HabrParser()
    try:
        yield parser
    finally:
        await parser.aclose()


async def get_redis_client() -> AsyncGenerator[Any, None]:
    """Предоставляет асинхронный клиент Redis"""
    redis_client: Optional[Any] = None
    try:
        redis_module = importlib.import_module("redis.asyncio")
        redis_client = redis_module.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True,
        )
        await redis_client.ping()
        logger.info("Подключение к Redis успешно установлено.")
        yield redis_client
    except Exception as e:
        logger.error(f"Не удалось подключиться к Redis: {e}")
        raise e
    finally:
        if redis_client is not None:
            await redis_client.close()
            logger.info("Подключение к Redis закрыто.")


@router.post("/parse", response_model=SArticleParsed)
async def parse_article(
    body: SParseRequest,
    parser: HabrParser = Depends(get_parser),
    session: AsyncSession = Depends(get_async_session),
    redis_client: Any = Depends(get_redis_client),
):
    url_str = str(body.url)

    # Проверяем статью в кэше
    if redis_client:
        try:
            cached_data = await redis_client.get(f"article:{url_str}")
            if cached_data:
                logger.info(f"Статья найдена в кэше: {url_str}")
                return SArticleParsed(**json.loads(cached_data))
        except Exception as e:
            logger.error(f"Ошибка Redis: {e}")

    # Проверяем статью в БД
    query = select(Article).where(Article.url == url_str)
    result = await session.execute(query)
    article_db = result.scalar_one_or_none()

    if article_db:
        logger.info(f"Статья найдена в БД: {url_str}")
        parsed_data = article_db.parsed_content
        # Сохраняем в кэш
        if redis_client:
            try:
                await redis_client.setex(
                    f"article:{url_str}", 3600, json.dumps(parsed_data)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        return SArticleParsed(**parsed_data)

    # Парсим статью если не нашли в кэше и БД
    data = await parser.get_article(url_str)
    if not data:
        raise HTTPException(
            status_code=400,
            detail="Не удалось распарсить статью по указанному URL",
        )

    try:
        parsed_article = SArticleParsed(**data)

        # Сохраняем в БД
        new_article = Article(url=url_str, parsed_content=data)
        session.add(new_article)
        await session.commit()

        # Сохраняем в кэше
        if redis_client:
            try:
                await redis_client.setex(
                    f"article:{url_str}", 3600, json.dumps(data)
                )
            except Exception as e:
                logger.error(f"Ошибка Redis при сохранении: {e}")

        return parsed_article
    except Exception as e:
        logger.error(f"Ошибка при обработке статьи: {e}")
        raise HTTPException(
            status_code=502, detail=f"Неверный формат распарсенных данных: {e}"
        )
