"""
Модель для коротких ссылок в QR сервисе.

Содержит SQLAlchemy модель для хранения информации о коротких ссылках
и связанных с ними QR кодах.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""
    pass


class ShortLink(Base):
    """
    Модель короткой ссылки.
    
    Хранит информацию о коротких ссылках, включая slug,
    тип цели, ID цели и статус активности.
    """
    
    __tablename__ = "short_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    target_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    extra_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """Строковое представление объекта."""
        return f"<ShortLink(id={self.id}, slug='{self.slug}', target_type='{self.target_type}')>"
