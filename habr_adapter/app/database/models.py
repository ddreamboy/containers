from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, TIMESTAMP, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Article(Base):
    __tablename__ = "articles"

    url: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    parsed_content: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
