from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, UTC
from typing import Optional

from app.database.base import Base


class Repository(Base):

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    github_id: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255)
    )

    owner: Mapped[str] = mapped_column(
        String(255)
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )

    language: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )

    stars: Mapped[int] = mapped_column(
        Integer
    )

    repo_url: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC)
    )