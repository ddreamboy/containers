from datetime import datetime

from sqlalchemy import JSON, TIMESTAMP, Integer, String, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True

    id: int = Integer(primary_key=True, autoincrement=True)
    created_at: datetime = TIMESTAMP(server_default=func.now())
    updated_at: datetime = TIMESTAMP(
        server_default=func.now(), onupdate=func.now()
    )


class Article(Base):
    __tablename__ = "articles"

    url: str = String(unique=True, index=True, nullable=False)
    parsed_content: dict = JSON(nullable=True)
