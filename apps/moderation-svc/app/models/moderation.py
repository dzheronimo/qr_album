"""
Модели модерации контента.

Содержит SQLAlchemy модели для работы с модерацией, AI анализом и правилами.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class ContentType(str, Enum):
    """Типы контента для модерации."""
    IMAGE = "image"
    TEXT = "text"
    VIDEO = "video"
    AUDIO = "audio"
    URL = "url"
    FILE = "file"


class ModerationStatus(str, Enum):
    """Статусы модерации."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    UNDER_REVIEW = "under_review"
    AUTO_APPROVED = "auto_approved"
    AUTO_REJECTED = "auto_rejected"


class ModerationType(str, Enum):
    """Типы модерации."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    AI = "ai"
    HYBRID = "hybrid"


class SeverityLevel(str, Enum):
    """Уровни серьезности нарушений."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModerationRequest(Base):
    """
    Модель запроса на модерацию.
    
    Содержит информацию о контенте, требующем модерации.
    """
    
    __tablename__ = "moderation_requests"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    content_type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType), nullable=False)
    
    # Информация о контенте
    content_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    content_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Настройки модерации
    moderation_type: Mapped[ModerationType] = mapped_column(SQLEnum(ModerationType), nullable=False, default=ModerationType.AUTOMATIC)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-5, где 5 - высший приоритет
    
    # Статус и результаты
    status: Mapped[ModerationStatus] = mapped_column(SQLEnum(ModerationStatus), nullable=False, default=ModerationStatus.PENDING)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Дополнительные данные
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Откуда поступил запрос
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Связи
    results: Mapped[list["ModerationResult"]] = relationship("ModerationResult", back_populates="request")
    logs: Mapped[list["ModerationLog"]] = relationship("ModerationLog", back_populates="request")
    
    def __repr__(self) -> str:
        """Строковое представление запроса."""
        return f"<ModerationRequest(id={self.id}, user_id={self.user_id}, type='{self.content_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_type": self.content_type.value,
            "content_id": self.content_id,
            "content_url": self.content_url,
            "content_text": self.content_text,
            "content_metadata": self.content_metadata,
            "moderation_type": self.moderation_type.value,
            "priority": self.priority,
            "status": self.status.value,
            "ai_confidence": self.ai_confidence,
            "context": self.context,
            "source": self.source,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


class ModerationResult(Base):
    """
    Модель результата модерации.
    
    Содержит результаты анализа контента.
    """
    
    __tablename__ = "moderation_results"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("moderation_requests.id"), nullable=False, index=True)
    
    # Результаты анализа
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Детали нарушений
    violations: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    violation_categories: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    severity_level: Mapped[Optional[SeverityLevel]] = mapped_column(SQLEnum(SeverityLevel), nullable=True)
    
    # AI анализ
    ai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Человеческая модерация
    moderator_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    moderator_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    human_override: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Дополнительные данные
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    request: Mapped["ModerationRequest"] = relationship("ModerationRequest", back_populates="results")
    
    def __repr__(self) -> str:
        """Строковое представление результата."""
        return f"<ModerationResult(id={self.id}, request_id={self.request_id}, approved={self.is_approved})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "is_approved": self.is_approved,
            "confidence_score": self.confidence_score,
            "risk_score": self.risk_score,
            "violations": self.violations,
            "violation_categories": self.violation_categories,
            "severity_level": self.severity_level.value if self.severity_level else None,
            "ai_model": self.ai_model,
            "ai_version": self.ai_version,
            "ai_analysis": self.ai_analysis,
            "moderator_id": self.moderator_id,
            "moderator_notes": self.moderator_notes,
            "human_override": self.human_override,
            "processing_time_ms": self.processing_time_ms,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ModerationRule(Base):
    """
    Модель правил модерации.
    
    Содержит настраиваемые правила для автоматической модерации.
    """
    
    __tablename__ = "moderation_rules"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Настройки правила
    content_type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Условия правила
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    threshold: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Действия
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # approve, reject, flag, review
    auto_action: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Дополнительные данные
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление правила."""
        return f"<ModerationRule(id={self.id}, name='{self.name}', type='{self.content_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "content_type": self.content_type.value,
            "is_active": self.is_active,
            "priority": self.priority,
            "conditions": self.conditions,
            "threshold": self.threshold,
            "action": self.action,
            "auto_action": self.auto_action,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ModerationLog(Base):
    """
    Модель журнала модерации.
    
    Содержит детальную историю всех действий модерации.
    """
    
    __tablename__ = "moderation_logs"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(Integer, ForeignKey("moderation_requests.id"), nullable=False, index=True)
    
    # Информация о действии
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # created, processed, approved, rejected, etc.
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user, ai, system, moderator
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
    request: Mapped["ModerationRequest"] = relationship("ModerationRequest", back_populates="logs")
    
    def __repr__(self) -> str:
        """Строковое представление записи журнала."""
        return f"<ModerationLog(id={self.id}, request_id={self.request_id}, action='{self.action}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "request_id": self.request_id,
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


class ModerationSettings(Base):
    """
    Модель настроек модерации.
    
    Содержит глобальные настройки системы модерации.
    """
    
    __tablename__ = "moderation_settings"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Настройки AI
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ai_models: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ai_thresholds: Mapped[Optional[Dict[str, float]]] = mapped_column(JSON, nullable=True)
    
    # Настройки автоматической модерации
    auto_moderation_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_approve_threshold: Mapped[float] = mapped_column(Float, default=0.9, nullable=False)
    auto_reject_threshold: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)
    
    # Настройки уведомлений
    notify_on_flag: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_on_reject: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Дополнительные настройки
    settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление настроек."""
        return f"<ModerationSettings(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "ai_enabled": self.ai_enabled,
            "ai_models": self.ai_models,
            "ai_thresholds": self.ai_thresholds,
            "auto_moderation_enabled": self.auto_moderation_enabled,
            "auto_approve_threshold": self.auto_approve_threshold,
            "auto_reject_threshold": self.auto_reject_threshold,
            "notify_on_flag": self.notify_on_flag,
            "notify_on_reject": self.notify_on_reject,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ContentFlag(Base):
    """
    Модель флагов контента.
    
    Содержит информацию о помеченном контенте.
    """
    
    __tablename__ = "content_flags"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    content_type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType), nullable=False)
    
    # Информация о флаге
    flag_type: Mapped[str] = mapped_column(String(50), nullable=False)  # inappropriate, spam, copyright, etc.
    severity: Mapped[SeverityLevel] = mapped_column(SQLEnum(SeverityLevel), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Кто пометил
    flagged_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # user_id или moderator_id
    flagged_by_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user, moderator, ai, system
    
    # Статус флага
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Дополнительные данные
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление флага."""
        return f"<ContentFlag(id={self.id}, content_id='{self.content_id}', type='{self.flag_type}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "content_id": self.content_id,
            "content_type": self.content_type.value,
            "flag_type": self.flag_type,
            "severity": self.severity.value,
            "reason": self.reason,
            "flagged_by": self.flagged_by,
            "flagged_by_type": self.flagged_by_type,
            "is_resolved": self.is_resolved,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution_notes": self.resolution_notes,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
