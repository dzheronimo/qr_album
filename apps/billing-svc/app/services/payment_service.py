"""
Сервис для работы с платежами.

Содержит бизнес-логику для обработки платежей.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.exc import IntegrityError

from app.models.billing import Payment, PaymentStatus, PaymentMethod, Transaction, TransactionType


class PaymentService:
    """Сервис для работы с платежами."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_payment(
        self,
        user_id: int,
        amount: Decimal,
        currency: str = "USD",
        payment_method: PaymentMethod = PaymentMethod.CARD,
        subscription_id: Optional[int] = None,
        description: Optional[str] = None,
        external_payment_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Payment:
        """
        Создание платежа.
        
        Args:
            user_id: ID пользователя
            amount: Сумма платежа
            currency: Валюта
            payment_method: Метод платежа
            subscription_id: ID подписки
            description: Описание платежа
            external_payment_id: Внешний ID платежа
            extra_data: Дополнительные данные
            
        Returns:
            Payment: Созданный платеж
        """
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            status=PaymentStatus.PENDING,
            description=description,
            external_payment_id=external_payment_id,
            extra_data=extra_data
        )
        
        try:
            self.db.add(payment)
            await self.db.commit()
            await self.db.refresh(payment)
            return payment
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании платежа")
    
    async def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Получение платежа по ID.
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Optional[Payment]: Платеж или None
        """
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_payment_by_external_id(self, external_payment_id: str) -> Optional[Payment]:
        """
        Получение платежа по внешнему ID.
        
        Args:
            external_payment_id: Внешний ID платежа
            
        Returns:
            Optional[Payment]: Платеж или None
        """
        result = await self.db.execute(
            select(Payment).where(Payment.external_payment_id == external_payment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_payments(
        self,
        user_id: int,
        status: Optional[PaymentStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Payment]:
        """
        Получение платежей пользователя.
        
        Args:
            user_id: ID пользователя
            status: Статус платежа для фильтрации
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[Payment]: Список платежей
        """
        query = select(Payment).where(Payment.user_id == user_id)
        
        if status:
            query = query.where(Payment.status == status)
        
        query = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_payment_status(
        self,
        payment_id: int,
        status: PaymentStatus,
        external_transaction_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Payment]:
        """
        Обновление статуса платежа.
        
        Args:
            payment_id: ID платежа
            status: Новый статус
            external_transaction_id: Внешний ID транзакции
            extra_data: Дополнительные данные
            
        Returns:
            Optional[Payment]: Обновленный платеж или None
        """
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            return None
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == PaymentStatus.COMPLETED:
            update_data["payment_date"] = datetime.utcnow()
            update_data["processed_at"] = datetime.utcnow()
        
        if external_transaction_id:
            update_data["external_transaction_id"] = external_transaction_id
        
        if extra_data:
            update_data["extra_data"] = extra_data
        
        await self.db.execute(
            update(Payment)
            .where(Payment.id == payment_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        # Создаем транзакцию
        await self._create_transaction(payment, status)
        
        return await self.get_payment_by_id(payment_id)
    
    async def _create_transaction(
        self,
        payment: Payment,
        status: PaymentStatus
    ) -> None:
        """
        Создание транзакции для платежа.
        
        Args:
            payment: Платеж
            status: Статус платежа
        """
        transaction_type = TransactionType.SUBSCRIPTION if payment.subscription_id else TransactionType.ONE_TIME
        
        if status == PaymentStatus.REFUNDED:
            transaction_type = TransactionType.REFUND
        
        transaction = Transaction(
            user_id=payment.user_id,
            payment_id=payment.id,
            subscription_id=payment.subscription_id,
            transaction_type=transaction_type,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description or f"Платеж #{payment.id}",
            external_transaction_id=payment.external_transaction_id,
            extra_data=payment.extra_data
        )
        
        self.db.add(transaction)
        await self.db.commit()
    
    async def process_payment(
        self,
        payment_id: int,
        external_transaction_id: Optional[str] = None
    ) -> bool:
        """
        Обработка платежа (заглушка).
        
        Args:
            payment_id: ID платежа
            external_transaction_id: Внешний ID транзакции
            
        Returns:
            bool: True если обработка успешна, False иначе
        """
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            return False
        
        # В реальном приложении здесь была бы интеграция с платежным провайдером
        # Для демонстрации просто помечаем платеж как успешный
        
        try:
            await self.update_payment_status(
                payment_id=payment_id,
                status=PaymentStatus.COMPLETED,
                external_transaction_id=external_transaction_id or f"txn_{payment_id}_{int(datetime.utcnow().timestamp())}"
            )
            return True
        except Exception:
            await self.update_payment_status(
                payment_id=payment_id,
                status=PaymentStatus.FAILED
            )
            return False
    
    async def refund_payment(
        self,
        payment_id: int,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> bool:
        """
        Возврат платежа.
        
        Args:
            payment_id: ID платежа
            amount: Сумма возврата (если не указана, возвращается полная сумма)
            reason: Причина возврата
            
        Returns:
            bool: True если возврат успешен, False иначе
        """
        payment = await self.get_payment_by_id(payment_id)
        if not payment:
            return False
        
        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Можно вернуть только завершенные платежи")
        
        refund_amount = amount or payment.amount
        
        try:
            # Обновляем статус платежа
            await self.update_payment_status(
                payment_id=payment_id,
                status=PaymentStatus.REFUNDED,
                extra_data={
                    **(payment.extra_data or {}),
                    "refund_amount": float(refund_amount),
                    "refund_reason": reason,
                    "refund_date": datetime.utcnow().isoformat()
                }
            )
            
            # Создаем транзакцию возврата
            refund_transaction = Transaction(
                user_id=payment.user_id,
                payment_id=payment.id,
                subscription_id=payment.subscription_id,
                transaction_type=TransactionType.REFUND,
                amount=-refund_amount,  # Отрицательная сумма для возврата
                currency=payment.currency,
                description=f"Возврат платежа #{payment.id}" + (f" - {reason}" if reason else ""),
                extra_data={
                    "original_payment_id": payment.id,
                    "refund_reason": reason
                }
            )
            
            self.db.add(refund_transaction)
            await self.db.commit()
            
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_payment_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получение статистики платежей пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Статистика платежей
        """
        # Общее количество платежей
        total_payments_result = await self.db.execute(
            select(func.count(Payment.id))
            .where(Payment.user_id == user_id)
        )
        total_payments = total_payments_result.scalar() or 0
        
        # Успешные платежи
        successful_payments_result = await self.db.execute(
            select(func.count(Payment.id))
            .where(
                and_(
                    Payment.user_id == user_id,
                    Payment.status == PaymentStatus.COMPLETED
                )
            )
        )
        successful_payments = successful_payments_result.scalar() or 0
        
        # Общая сумма платежей
        total_amount_result = await self.db.execute(
            select(func.sum(Payment.amount))
            .where(
                and_(
                    Payment.user_id == user_id,
                    Payment.status == PaymentStatus.COMPLETED
                )
            )
        )
        total_amount = total_amount_result.scalar() or 0
        
        # Платежи по статусам
        payments_by_status_result = await self.db.execute(
            select(
                Payment.status,
                func.count(Payment.id).label('count')
            )
            .where(Payment.user_id == user_id)
            .group_by(Payment.status)
        )
        payments_by_status = {row.status.value: row.count for row in payments_by_status_result}
        
        # Платежи по методам
        payments_by_method_result = await self.db.execute(
            select(
                Payment.payment_method,
                func.count(Payment.id).label('count')
            )
            .where(Payment.user_id == user_id)
            .group_by(Payment.payment_method)
        )
        payments_by_method = {row.payment_method.value: row.count for row in payments_by_method_result}
        
        return {
            "user_id": user_id,
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "total_amount": float(total_amount),
            "payments_by_status": payments_by_status,
            "payments_by_method": payments_by_method
        }
