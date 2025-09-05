"""
Модели профилей пользователей.

Содержит SQLAlchemy модели для работы с профилями и настройками пользователей.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class ThemeType(str, Enum):
    """Типы тем оформления."""
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"


class LanguageType(str, Enum):
    """Поддерживаемые языки."""
    RU = "ru"
    EN = "en"
    DE = "de"
    FR = "fr"
    ES = "es"


class UserProfile(Base):
    """
    Модель профиля пользователя.
    
    Содержит расширенную информацию о пользователе, не связанную с аутентификацией.
    """
    
    __tablename__ = "user_profiles"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    
    # Личная информация
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Контактная информация
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Аватар и медиа
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Социальные сети
    social_links: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Настройки приватности
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_phone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_location: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        """Строковое представление профиля."""
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, display_name='{self.display_name}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "display_name": self.display_name,
            "bio": self.bio,
            "phone": self.phone,
            "website": self.website,
            "location": self.location,
            "timezone": self.timezone,
            "avatar_url": self.avatar_url,
            "cover_image_url": self.cover_image_url,
            "social_links": self.social_links,
            "is_public": self.is_public,
            "show_email": self.show_email,
            "show_phone": self.show_phone,
            "show_location": self.show_location,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_seen_at": self.last_seen_at.isoformat() if self.last_seen_at else None,
        }
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(filter(None, parts)) or self.display_name or f"User {self.user_id}"
    
    @property
    def initials(self) -> str:
        """Инициалы пользователя."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.display_name:
            return self.display_name[:2].upper()
        else:
            return f"U{self.user_id}"


class UserSettings(Base):
    """
    Модель настроек пользователя.
    
    Содержит пользовательские настройки интерфейса и поведения приложения.
    """
    
    __tablename__ = "user_settings"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    
    # Настройки интерфейса
    theme: Mapped[ThemeType] = mapped_column(SQLEnum(ThemeType), default=ThemeType.AUTO, nullable=False)
    language: Mapped[LanguageType] = mapped_column(SQLEnum(LanguageType), default=LanguageType.RU, nullable=False)
    
    # Настройки уведомлений
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    push_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Настройки приватности
    profile_visibility: Mapped[str] = mapped_column(String(20), default="public", nullable=False)
    album_visibility: Mapped[str] = mapped_column(String(20), default="public", nullable=False)
    allow_following: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Настройки безопасности
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    login_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Настройки контента
    auto_save_drafts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    compress_images: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_file_size_mb: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    
    # Дополнительные настройки
    custom_settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление настроек."""
        return f"<UserSettings(id={self.id}, user_id={self.user_id}, theme='{self.theme}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "theme": self.theme.value,
            "language": self.language.value,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "sms_notifications": self.sms_notifications,
            "profile_visibility": self.profile_visibility,
            "album_visibility": self.album_visibility,
            "allow_following": self.allow_following,
            "two_factor_enabled": self.two_factor_enabled,
            "login_notifications": self.login_notifications,
            "auto_save_drafts": self.auto_save_drafts,
            "compress_images": self.compress_images,
            "max_file_size_mb": self.max_file_size_mb,
            "custom_settings": self.custom_settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
