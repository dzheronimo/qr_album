"""
Модели уведомлений.

Содержит SQLAlchemy модели для работы с уведомлениями, шаблонами и настройками.
"""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class NotificationType(str, Enum):
    """Типы уведомлений."""
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationStatus(str, Enum):
    """Статусы уведомлений."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationPriority(str, Enum):
    """Приоритеты уведомлений."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationTemplate(Base):
    """
    Модель шаблона уведомления.
    
    Содержит шаблоны для различных типов уведомлений.
    """
    
    __tablename__ = "notification_templates"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Настройки шаблона
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Переменные для подстановки
    
    # Метаданные
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="template")
    
    def __repr__(self) -> str:
        """Строковое представление шаблона."""
        return f"<NotificationTemplate(id={self.id}, name='{self.name}', type='{self.notification_type}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "name": self.name,
            "notification_type": self.notification_type.value,
            "subject": self.subject,
            "content": self.content,
            "is_active": self.is_active,
            "variables": self.variables,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Notification(Base):
    """
    Модель уведомления.
    
    Отслеживает отправленные и запланированные уведомления.
    """
    
    __tablename__ = "notifications"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("notification_templates.id"), nullable=True, index=True)
    
    # Содержимое уведомления
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Получатель
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    recipient_device_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Статус и приоритет
    status: Mapped[NotificationStatus] = mapped_column(SQLEnum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING)
    priority: Mapped[NotificationPriority] = mapped_column(SQLEnum(NotificationPriority), nullable=False, default=NotificationPriority.NORMAL)
    
    # Временные метки
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    template: Mapped[Optional["NotificationTemplate"]] = relationship("NotificationTemplate", back_populates="notifications")
    
    def __repr__(self) -> str:
        """Строковое представление уведомления."""
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.notification_type}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "template_id": self.template_id,
            "template": self.template.to_dict() if self.template else None,
            "notification_type": self.notification_type.value,
            "subject": self.subject,
            "content": self.content,
            "recipient_email": self.recipient_email,
            "recipient_phone": self.recipient_phone,
            "recipient_device_token": self.recipient_device_token,
            "status": self.status.value,
            "priority": self.priority.value,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "extra_data": self.extra_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NotificationSettings(Base):
    """
    Модель настроек уведомлений пользователя.
    
    Содержит настройки пользователя для различных типов уведомлений.
    """
    
    __tablename__ = "notification_settings"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, unique=True)
    
    # Настройки по типам уведомлений
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Настройки по категориям
    marketing_emails: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    system_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    security_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    billing_notifications: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Дополнительные настройки
    quiet_hours_start: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # HH:MM
    quiet_hours_end: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)    # HH:MM
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление настроек."""
        return f"<NotificationSettings(id={self.id}, user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_enabled": self.email_enabled,
            "push_enabled": self.push_enabled,
            "sms_enabled": self.sms_enabled,
            "in_app_enabled": self.in_app_enabled,
            "marketing_emails": self.marketing_emails,
            "system_notifications": self.system_notifications,
            "security_alerts": self.security_alerts,
            "billing_notifications": self.billing_notifications,
            "quiet_hours_start": self.quiet_hours_start,
            "quiet_hours_end": self.quiet_hours_end,
            "timezone": self.timezone,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class NotificationQueue(Base):
    """
    Модель очереди уведомлений.
    
    Содержит уведомления, ожидающие отправки.
    """
    
    __tablename__ = "notification_queue"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    notification_id: Mapped[int] = mapped_column(Integer, ForeignKey("notifications.id"), nullable=False, index=True)
    
    # Настройки очереди
    priority: Mapped[NotificationPriority] = mapped_column(SQLEnum(NotificationPriority), nullable=False, default=NotificationPriority.NORMAL)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Статус обработки
    is_processing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    notification: Mapped["Notification"] = relationship("Notification")
    
    def __repr__(self) -> str:
        """Строковое представление элемента очереди."""
        return f"<NotificationQueue(id={self.id}, notification_id={self.notification_id}, scheduled_at='{self.scheduled_at}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "notification_id": self.notification_id,
            "notification": self.notification.to_dict() if self.notification else None,
            "priority": self.priority.value,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "is_processing": self.is_processing,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
