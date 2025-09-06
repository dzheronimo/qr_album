"""
Модели для работы с печатью и PDF генерацией.

Содержит SQLAlchemy модели для управления заданиями печати, шаблонами и очередями.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class PrintJobStatus(str, Enum):
    """Статусы заданий печати."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PrintJobType(str, Enum):
    """Типы заданий печати."""
    QR_LABEL = "qr_label"
    ALBUM_COVER = "album_cover"
    PAGE_THUMBNAIL = "page_thumbnail"
    CUSTOM_TEMPLATE = "custom_template"


class PrintFormat(str, Enum):
    """Форматы печати."""
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"


class PrintJob(Base):
    """
    Модель задания печати.
    
    Содержит информацию о задании на генерацию PDF или изображений.
    """
    
    __tablename__ = "print_jobs"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    job_type: Mapped[PrintJobType] = mapped_column(SQLEnum(PrintJobType), nullable=False)
    
    # Параметры задания
    template_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("print_templates.id"), nullable=True)
    layout_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("print_layouts.id"), nullable=True)
    
    # Контент для печати
    content_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    print_format: Mapped[PrintFormat] = mapped_column(SQLEnum(PrintFormat), nullable=False, default=PrintFormat.PDF)
    
    # Настройки печати
    page_size: Mapped[str] = mapped_column(String(20), nullable=False, default="A4")
    orientation: Mapped[str] = mapped_column(String(10), nullable=False, default="portrait")  # portrait, landscape
    quality: Mapped[int] = mapped_column(Integer, default=300, nullable=False)  # DPI
    
    # Статус и результаты
    status: Mapped[PrintJobStatus] = mapped_column(SQLEnum(PrintJobStatus), nullable=False, default=PrintJobStatus.PENDING)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0-100
    
    # Результаты
    output_file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    output_file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Ошибки
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Дополнительные данные
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-5, где 5 - высший приоритет
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Связи
    template: Mapped[Optional["PrintTemplate"]] = relationship("PrintTemplate", back_populates="jobs")
    layout: Mapped[Optional["PrintLayout"]] = relationship("PrintLayout", back_populates="jobs")
    history: Mapped[list["PrintHistory"]] = relationship("PrintHistory", back_populates="job")
    
    def __repr__(self) -> str:
        """Строковое представление задания."""
        return f"<PrintJob(id={self.id}, user_id={self.user_id}, type='{self.job_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_type": self.job_type.value,
            "template_id": self.template_id,
            "layout_id": self.layout_id,
            "content_data": self.content_data,
            "print_format": self.print_format.value,
            "page_size": self.page_size,
            "orientation": self.orientation,
            "quality": self.quality,
            "status": self.status.value,
            "progress": self.progress,
            "output_file_path": self.output_file_path,
            "output_file_size": self.output_file_size,
            "output_url": self.output_url,
            "error_message": self.error_message,
            "error_details": self.error_details,
            "extra_metadata": self.extra_metadata,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class PrintTemplate(Base):
    """
    Модель шаблона печати.
    
    Содержит HTML/CSS шаблоны для генерации PDF.
    """
    
    __tablename__ = "print_templates"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Тип и категория
    template_type: Mapped[PrintJobType] = mapped_column(SQLEnum(PrintJobType), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Шаблон
    html_template: Mapped[str] = mapped_column(Text, nullable=False)
    css_styles: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Настройки
    default_page_size: Mapped[str] = mapped_column(String(20), nullable=False, default="A4")
    default_orientation: Mapped[str] = mapped_column(String(10), nullable=False, default="portrait")
    default_quality: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    
    # Параметры шаблона
    template_variables: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    required_fields: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Системный шаблон
    
    # Дополнительные данные
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    jobs: Mapped[list["PrintJob"]] = relationship("PrintJob", back_populates="template")
    
    def __repr__(self) -> str:
        """Строковое представление шаблона."""
        return f"<PrintTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "template_type": self.template_type.value,
            "category": self.category,
            "html_template": self.html_template,
            "css_styles": self.css_styles,
            "default_page_size": self.default_page_size,
            "default_orientation": self.default_orientation,
            "default_quality": self.default_quality,
            "template_variables": self.template_variables,
            "required_fields": self.required_fields,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PrintLayout(Base):
    """
    Модель макета печати.
    
    Содержит настройки расположения элементов на странице.
    """
    
    __tablename__ = "print_layouts"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Тип макета
    layout_type: Mapped[PrintJobType] = mapped_column(SQLEnum(PrintJobType), nullable=False)
    
    # Настройки макета
    page_width: Mapped[float] = mapped_column(Float, nullable=False)
    page_height: Mapped[float] = mapped_column(Float, nullable=False)
    margin_top: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    margin_bottom: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    margin_left: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    margin_right: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    
    # Элементы макета
    elements: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Дополнительные данные
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    jobs: Mapped[list["PrintJob"]] = relationship("PrintJob", back_populates="layout")
    
    def __repr__(self) -> str:
        """Строковое представление макета."""
        return f"<PrintLayout(id={self.id}, name='{self.name}', type='{self.layout_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "layout_type": self.layout_type.value,
            "page_width": self.page_width,
            "page_height": self.page_height,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "margin_left": self.margin_left,
            "margin_right": self.margin_right,
            "elements": self.elements,
            "is_active": self.is_active,
            "is_system": self.is_system,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PrintQueue(Base):
    """
    Модель очереди печати.
    
    Содержит задания, ожидающие обработки.
    """
    
    __tablename__ = "print_queue"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("print_jobs.id"), nullable=False, unique=True)
    
    # Приоритет и планирование
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Статус обработки
    is_processing: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    worker_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Попытки обработки
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    job: Mapped["PrintJob"] = relationship("PrintJob")
    
    def __repr__(self) -> str:
        """Строковое представление элемента очереди."""
        return f"<PrintQueue(id={self.id}, job_id={self.job_id}, priority={self.priority})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "priority": self.priority,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "is_processing": self.is_processing,
            "worker_id": self.worker_id,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PrintSettings(Base):
    """
    Модель настроек печати.
    
    Содержит глобальные настройки системы печати.
    """
    
    __tablename__ = "print_settings"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Настройки WeasyPrint
    weasyprint_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weasyprint_timeout: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    weasyprint_retry_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Настройки очереди
    queue_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    queue_cleanup_interval: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)  # секунды
    
    # Настройки файлов
    output_directory: Mapped[str] = mapped_column(String(500), nullable=False, default="/tmp/print_output")
    file_retention_days: Mapped[int] = mapped_column(Integer, default=7, nullable=False)
    max_file_size_mb: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    # Настройки качества
    default_quality: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    supported_formats: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=["pdf", "png", "jpg"])
    supported_page_sizes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=["A4", "A5", "Letter"])
    
    # Дополнительные настройки
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление настроек."""
        return f"<PrintSettings(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "weasyprint_enabled": self.weasyprint_enabled,
            "weasyprint_timeout": self.weasyprint_timeout,
            "weasyprint_retry_attempts": self.weasyprint_retry_attempts,
            "queue_enabled": self.queue_enabled,
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "queue_cleanup_interval": self.queue_cleanup_interval,
            "output_directory": self.output_directory,
            "file_retention_days": self.file_retention_days,
            "max_file_size_mb": self.max_file_size_mb,
            "default_quality": self.default_quality,
            "supported_formats": self.supported_formats,
            "supported_page_sizes": self.supported_page_sizes,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PrintHistory(Base):
    """
    Модель истории печати.
    
    Содержит детальную историю всех операций печати.
    """
    
    __tablename__ = "print_history"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("print_jobs.id"), nullable=False, index=True)
    
    # Информация о действии
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # created, started, completed, failed, etc.
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user, system, worker
    actor_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Детали действия
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Дополнительные данные
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Связи
    job: Mapped["PrintJob"] = relationship("PrintJob", back_populates="history")
    
    def __repr__(self) -> str:
        """Строковое представление записи истории."""
        return f"<PrintHistory(id={self.id}, job_id={self.job_id}, action='{self.action}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "action": self.action,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "details": self.details,
            "message": self.message,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
