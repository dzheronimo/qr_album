"""
Модель медиафайла для Media сервиса.

Содержит SQLAlchemy модель для работы с медиафайлами.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class MediaType(str, Enum):
    """Типы медиафайлов."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"


class MediaStatus(str, Enum):
    """Статусы медиафайлов."""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


class MediaFile(Base):
    """
    Модель медиафайла.
    
    Содержит информацию о медиафайле, включая метаданные и ссылки на хранилище.
    """
    
    __tablename__ = "media_files"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Связь с пользователем и страницей
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    page_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    album_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Информация о файле
    file_type: Mapped[MediaType] = mapped_column(SQLEnum(MediaType), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # в байтах
    
    # Ссылки на хранилище
    s3_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    s3_bucket: Mapped[str] = mapped_column(String(100), nullable=False)
    s3_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Метаданные для изображений
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # для видео/аудио
    
    # Статус и обработка
    status: Mapped[MediaStatus] = mapped_column(SQLEnum(MediaStatus), default=MediaStatus.UPLOADING, nullable=False)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Теги и описание
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON строка с тегами
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление медиафайла."""
        return f"<MediaFile(id={self.id}, filename='{self.filename}', type='{self.file_type}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "user_id": self.user_id,
            "page_id": self.page_id,
            "album_id": self.album_id,
            "file_type": self.file_type.value,
            "mime_type": self.mime_type,
            "file_size": self.file_size,
            "s3_key": self.s3_key,
            "s3_bucket": self.s3_bucket,
            "s3_url": self.s3_url,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "status": self.status.value,
            "processing_error": self.processing_error,
            "tags": self.tags,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def file_size_mb(self) -> float:
        """Размер файла в мегабайтах."""
        return self.file_size / (1024 * 1024)
    
    @property
    def is_image(self) -> bool:
        """Проверка, является ли файл изображением."""
        return self.file_type == MediaType.IMAGE
    
    @property
    def is_video(self) -> bool:
        """Проверка, является ли файл видео."""
        return self.file_type == MediaType.VIDEO
    
    @property
    def is_audio(self) -> bool:
        """Проверка, является ли файл аудио."""
        return self.file_type == MediaType.AUDIO
    
    @property
    def aspect_ratio(self) -> Optional[float]:
        """Соотношение сторон для изображений/видео."""
        if self.width and self.height and self.height > 0:
            return self.width / self.height
        return None
