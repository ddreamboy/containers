import os
from contextlib import asynccontextmanager

from app.article_parser.api import router as habr_router
from app.core.logging_config import setup_logging
from config import settings
from fastapi import FastAPI
from loguru import logger

setup_logging()


def ensure_dirs():
    dirs = [
        settings.LOGS_DIR,
    ]
    for d in dirs:
        logger.info(f"Проверка и создание директории: {d}")
        os.makedirs(d, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Инициализация приложения...")
        ensure_dirs()

        logger.info("Приложение успешно запущено")
        yield

    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        raise
    finally:
        try:
            logger.info("Завершение работы приложения...")
            logger.info("Работа корректно завершена")
        except Exception as e:
            logger.error(f"Ошибка при завершении: {e}")


app = FastAPI(
    title="Habr Adapter",
    lifespan=lifespan,
)

app.include_router(habr_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.HABR_ADAPTER_PORT)
