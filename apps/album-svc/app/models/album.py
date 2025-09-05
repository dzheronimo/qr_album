"""
Модели альбомов и страниц для Album сервиса.

Содержит SQLAlchemy модели для работы с альбомами и страницами.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class AlbumStatus(str, Enum):
    """Статусы альбома."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PageStatus(str, Enum):
    """Статусы страницы."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Album(Base):
    """
    Модель альбома.
    
    Содержит информацию об альбоме, включая метаданные и настройки.
    """
    
    __tablename__ = "albums"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Связь с пользователем
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Статус и настройки
    status: Mapped[AlbumStatus] = mapped_column(SQLEnum(AlbumStatus), default=AlbumStatus.DRAFT, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Метаданные
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON строка с тегами
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Связи
    pages: Mapped[List["Page"]] = relationship("Page", back_populates="album", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """Строковое представление альбома."""
        return f"<Album(id={self.id}, title='{self.title}', user_id={self.user_id}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "status": self.status.value,
            "is_public": self.is_public,
            "cover_image_url": self.cover_image_url,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "pages_count": 0,  # Будет заполнено отдельным запросом
        }


class Page(Base):
    """
    Модель страницы альбома.
    
    Содержит информацию о странице альбома, включая контент и медиафайлы.
    """
    
    __tablename__ = "pages"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Связь с альбомом
    album_id: Mapped[int] = mapped_column(Integer, ForeignKey("albums.id"), nullable=False, index=True)
    
    # Порядок страницы в альбоме
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Статус
    status: Mapped[PageStatus] = mapped_column(SQLEnum(PageStatus), default=PageStatus.DRAFT, nullable=False)
    
    # Метаданные
    background_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # HEX цвет
    text_color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # HEX цвет
    font_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    font_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    album: Mapped["Album"] = relationship("Album", back_populates="pages")
    
    def __repr__(self) -> str:
        """Строковое представление страницы."""
        return f"<Page(id={self.id}, title='{self.title}', album_id={self.album_id}, order_index={self.order_index})>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "album_id": self.album_id,
            "order_index": self.order_index,
            "status": self.status.value,
            "background_color": self.background_color,
            "text_color": self.text_color,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
