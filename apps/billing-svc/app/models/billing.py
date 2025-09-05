"""
Модели биллинга.

Содержит SQLAlchemy модели для работы с подписками, платежами, транзакциями и тарифами.
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal

from sqlalchemy import String, Boolean, DateTime, Text, Integer, JSON, Enum as SQLEnum, Numeric, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class PlanType(str, Enum):
    """Типы тарифных планов."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Статусы подписок."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    PENDING = "pending"


class PaymentStatus(str, Enum):
    """Статусы платежей."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    """Методы платежей."""
    CARD = "card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    MANUAL = "manual"


class TransactionType(str, Enum):
    """Типы транзакций."""
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"
    REFUND = "refund"
    CREDIT = "credit"
    DEBIT = "debit"


class Plan(Base):
    """
    Модель тарифного плана.
    
    Содержит информацию о доступных тарифных планах.
    """
    
    __tablename__ = "plans"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    plan_type: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Ценообразование
    price_monthly: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    price_yearly: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    
    # Лимиты
    max_albums: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_pages_per_album: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_media_files: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_qr_codes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_storage_gb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Функции
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="plan")
    
    def __repr__(self) -> str:
        """Строковое представление плана."""
        return f"<Plan(id={self.id}, name='{self.name}', type='{self.plan_type}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "name": self.name,
            "plan_type": self.plan_type.value,
            "description": self.description,
            "price_monthly": float(self.price_monthly),
            "price_yearly": float(self.price_yearly) if self.price_yearly else None,
            "currency": self.currency,
            "max_albums": self.max_albums,
            "max_pages_per_album": self.max_pages_per_album,
            "max_media_files": self.max_media_files,
            "max_qr_codes": self.max_qr_codes,
            "max_storage_gb": self.max_storage_gb,
            "features": self.features,
            "is_active": self.is_active,
            "is_popular": self.is_popular,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Subscription(Base):
    """
    Модель подписки пользователя.
    
    Отслеживает подписки пользователей на тарифные планы.
    """
    
    __tablename__ = "subscriptions"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"), nullable=False, index=True)
    
    # Статус и периодичность
    status: Mapped[SubscriptionStatus] = mapped_column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False, default="monthly")  # monthly, yearly
    
    # Даты
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_billing_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Автопродление
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    plan: Mapped["Plan"] = relationship("Plan", back_populates="subscriptions")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="subscription")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="subscription")
    
    def __repr__(self) -> str:
        """Строковое представление подписки."""
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan_id={self.plan_id}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_id": self.plan_id,
            "plan": None,  # Будет загружено отдельно при необходимости
            "status": self.status.value,
            "billing_cycle": self.billing_cycle,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_billing_date": self.next_billing_date.isoformat() if self.next_billing_date else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "auto_renew": self.auto_renew,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def is_active(self) -> bool:
        """Проверяет, активна ли подписка."""
        return self.status == SubscriptionStatus.ACTIVE and (
            self.end_date is None or self.end_date > datetime.utcnow()
        )


class Payment(Base):
    """
    Модель платежа.
    
    Отслеживает платежи пользователей.
    """
    
    __tablename__ = "payments"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    subscription_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("subscriptions.id"), nullable=True, index=True)
    
    # Информация о платеже
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(SQLEnum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Внешние идентификаторы
    external_payment_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, unique=True)
    external_transaction_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Описание
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Даты
    payment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    subscription: Mapped[Optional["Subscription"]] = relationship("Subscription", back_populates="payments")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="payment")
    
    def __repr__(self) -> str:
        """Строковое представление платежа."""
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_id": self.subscription_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "payment_method": self.payment_method.value,
            "status": self.status.value,
            "external_payment_id": self.external_payment_id,
            "external_transaction_id": self.external_transaction_id,
            "description": self.description,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Transaction(Base):
    """
    Модель транзакции.
    
    Отслеживает все финансовые транзакции.
    """
    
    __tablename__ = "transactions"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    payment_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("payments.id"), nullable=True, index=True)
    subscription_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("subscriptions.id"), nullable=True, index=True)
    
    # Информация о транзакции
    transaction_type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    
    # Описание
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Внешние идентификаторы
    external_transaction_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Связи
    payment: Mapped[Optional["Payment"]] = relationship("Payment", back_populates="transactions")
    subscription: Mapped[Optional["Subscription"]] = relationship("Subscription", back_populates="transactions")
    
    def __repr__(self) -> str:
        """Строковое представление транзакции."""
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type='{self.transaction_type}', amount={self.amount})>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "payment_id": self.payment_id,
            "subscription_id": self.subscription_id,
            "transaction_type": self.transaction_type.value,
            "amount": float(self.amount),
            "currency": self.currency,
            "description": self.description,
            "external_transaction_id": self.external_transaction_id,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Usage(Base):
    """
    Модель использования ресурсов.
    
    Отслеживает использование ресурсов пользователями.
    """
    
    __tablename__ = "usage"
    
    # Основные поля
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Использование ресурсов
    albums_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pages_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    media_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    qr_codes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    storage_used_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Период
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Дополнительные данные
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """Строковое представление использования."""
        return f"<Usage(id={self.id}, user_id={self.user_id}, albums={self.albums_count})>"
    
    def to_dict(self) -> dict:
        """Преобразование в словарь для API."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "albums_count": self.albums_count,
            "pages_count": self.pages_count,
            "media_files_count": self.media_files_count,
            "qr_codes_count": self.qr_codes_count,
            "storage_used_mb": self.storage_used_mb,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
