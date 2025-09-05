"""
Модели аналитики.

Содержит SQLAlchemy модели для отслеживания сканирований, активности пользователей и просмотров.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, Enum as SQLEnum, Float, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class EventType(str, Enum):
    """Типы событий аналитики."""
    SCAN = "scan"
    PAGE_VIEW = "page_view"
    ALBUM_VIEW = "album_view"
    DOWNLOAD = "download"
    SHARE = "share"
    LIKE = "like"
    COMMENT = "comment"


class DeviceType(str, Enum):
    """Типы устройств."""
    MOBILE = "mobile"
    TABLET = "tablet"
    DESKTOP = "desktop"
    UNKNOWN = "unknown"


class ScanEvent(Base):
    """
    Модель события сканирования QR кода.
    
    Отслеживает каждое сканирование QR кода с детальной информацией.
    """
    
    __tablename__ = "scan_events"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    qr_code_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Информация о сканировании
    scan_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 support
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Геолокация
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Устройство и браузер
    device_type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), default=DeviceType.UNKNOWN, nullable=False)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Дополнительные данные
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        """Строковое представление события сканирования."""
        return f"<ScanEvent(id={self.id}, qr_code_id={self.qr_code_id}, timestamp='{self.scan_timestamp}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "qr_code_id": self.qr_code_id,
            "user_id": self.user_id,
            "scan_timestamp": self.scan_timestamp.isoformat() if self.scan_timestamp else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referer": self.referer,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "device_type": self.device_type.value,
            "browser": self.browser,
            "os": self.os,
            "session_id": self.session_id,
            "extra_data": self.extra_data,
        }


class UserActivity(Base):
    """
    Модель активности пользователя.
    
    Отслеживает общую активность пользователей в системе.
    """
    
    __tablename__ = "user_activities"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType), nullable=False, index=True)
    
    # Информация о событии
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # ID связанной сущности
    entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Тип сущности (album, page, etc.)
    
    # Контекст
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        """Строковое представление активности пользователя."""
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, event_type='{self.event_type}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type.value,
            "event_timestamp": self.event_timestamp.isoformat() if self.event_timestamp else None,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "extra_data": self.extra_data,
        }


class PageView(Base):
    """
    Модель просмотра страницы.
    
    Отслеживает просмотры страниц альбомов.
    """
    
    __tablename__ = "page_views"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    page_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Информация о просмотре
    view_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Время на странице
    is_unique: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Уникальный просмотр
    
    # Контекст
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Геолокация
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Устройство
    device_type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), default=DeviceType.UNKNOWN, nullable=False)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    def __repr__(self) -> str:
        """Строковое представление просмотра страницы."""
        return f"<PageView(id={self.id}, page_id={self.page_id}, timestamp='{self.view_timestamp}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "page_id": self.page_id,
            "user_id": self.user_id,
            "view_timestamp": self.view_timestamp.isoformat() if self.view_timestamp else None,
            "duration_seconds": self.duration_seconds,
            "is_unique": self.is_unique,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referer": self.referer,
            "session_id": self.session_id,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "device_type": self.device_type.value,
            "browser": self.browser,
            "os": self.os,
        }


class AlbumView(Base):
    """
    Модель просмотра альбома.
    
    Отслеживает просмотры альбомов.
    """
    
    __tablename__ = "album_views"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    album_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    # Информация о просмотре
    view_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Время в альбоме
    pages_viewed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Количество просмотренных страниц
    is_unique: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Уникальный просмотр
    
    # Контекст
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Геолокация
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Устройство
    device_type: Mapped[DeviceType] = mapped_column(SQLEnum(DeviceType), default=DeviceType.UNKNOWN, nullable=False)
    browser: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    def __repr__(self) -> str:
        """Строковое представление просмотра альбома."""
        return f"<AlbumView(id={self.id}, album_id={self.album_id}, timestamp='{self.view_timestamp}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "album_id": self.album_id,
            "user_id": self.user_id,
            "view_timestamp": self.view_timestamp.isoformat() if self.view_timestamp else None,
            "duration_seconds": self.duration_seconds,
            "pages_viewed": self.pages_viewed,
            "is_unique": self.is_unique,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referer": self.referer,
            "session_id": self.session_id,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "device_type": self.device_type.value,
            "browser": self.browser,
            "os": self.os,
        }


# Создание индексов для оптимизации запросов
Index('idx_scan_events_qr_timestamp', ScanEvent.qr_code_id, ScanEvent.scan_timestamp)
Index('idx_scan_events_user_timestamp', ScanEvent.user_id, ScanEvent.scan_timestamp)
Index('idx_user_activities_user_timestamp', UserActivity.user_id, UserActivity.event_timestamp)
Index('idx_page_views_page_timestamp', PageView.page_id, PageView.view_timestamp)
Index('idx_album_views_album_timestamp', AlbumView.album_id, AlbumView.view_timestamp)
