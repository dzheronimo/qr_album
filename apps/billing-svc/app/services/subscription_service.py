"""
Сервис для работы с подписками.

Содержит бизнес-логику для управления подписками пользователей.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.models.billing import Subscription, Plan, SubscriptionStatus, PlanType


class SubscriptionService:
    """Сервис для работы с подписками."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_subscription(
        self,
        user_id: int,
        plan_id: int,
        billing_cycle: str = "monthly",
        auto_renew: bool = True,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Subscription:
        """
        Создание подписки пользователя.
        
        Args:
            user_id: ID пользователя
            plan_id: ID тарифного плана
            billing_cycle: Цикл биллинга (monthly, yearly)
            auto_renew: Автопродление
            extra_data: Дополнительные данные
            
        Returns:
            Subscription: Созданная подписка
            
        Raises:
            ValueError: Если план не найден или пользователь уже имеет активную подписку
        """
        # Проверяем, что план существует
        plan = await self.get_plan_by_id(plan_id)
        if not plan:
            raise ValueError("Тарифный план не найден")
        
        # Проверяем, что у пользователя нет активной подписки
        existing_subscription = await self.get_active_subscription(user_id)
        if existing_subscription:
            raise ValueError("У пользователя уже есть активная подписка")
        
        # Вычисляем даты
        start_date = datetime.utcnow()
        if billing_cycle == "yearly":
            end_date = start_date + timedelta(days=365)
            next_billing_date = end_date
        else:  # monthly
            end_date = start_date + timedelta(days=30)
            next_billing_date = end_date
        
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE,
            billing_cycle=billing_cycle,
            start_date=start_date,
            end_date=end_date,
            next_billing_date=next_billing_date,
            auto_renew=auto_renew,
            extra_data=extra_data
        )
        
        try:
            self.db.add(subscription)
            await self.db.commit()
            await self.db.refresh(subscription)
            return subscription
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании подписки")
    
    async def get_subscription_by_id(self, subscription_id: int) -> Optional[Subscription]:
        """
        Получение подписки по ID.
        
        Args:
            subscription_id: ID подписки
            
        Returns:
            Optional[Subscription]: Подписка или None
        """
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """
        Получение активной подписки пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Subscription]: Активная подписка или None
        """
        result = await self.db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    or_(
                        Subscription.end_date.is_(None),
                        Subscription.end_date > datetime.utcnow()
                    )
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_subscriptions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Subscription]:
        """
        Получение всех подписок пользователя.
        
        Args:
            user_id: ID пользователя
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[Subscription]: Список подписок
        """
        result = await self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_subscription(
        self,
        subscription_id: int,
        status: Optional[SubscriptionStatus] = None,
        auto_renew: Optional[bool] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Subscription]:
        """
        Обновление подписки.
        
        Args:
            subscription_id: ID подписки
            status: Новый статус
            auto_renew: Автопродление
            extra_data: Дополнительные данные
            
        Returns:
            Optional[Subscription]: Обновленная подписка или None
        """
        subscription = await self.get_subscription_by_id(subscription_id)
        if not subscription:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if status is not None:
            update_data["status"] = status
            if status == SubscriptionStatus.CANCELLED:
                update_data["cancelled_at"] = datetime.utcnow()
        
        if auto_renew is not None:
            update_data["auto_renew"] = auto_renew
        
        if extra_data is not None:
            update_data["extra_data"] = extra_data
        
        if not update_data:
            return subscription
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_subscription_by_id(subscription_id)
    
    async def cancel_subscription(self, subscription_id: int) -> bool:
        """
        Отмена подписки.
        
        Args:
            subscription_id: ID подписки
            
        Returns:
            bool: True если отмена успешна, False иначе
        """
        subscription = await self.get_subscription_by_id(subscription_id)
        if not subscription:
            return False
        
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(
                status=SubscriptionStatus.CANCELLED,
                cancelled_at=datetime.utcnow(),
                auto_renew=False,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def renew_subscription(self, subscription_id: int) -> bool:
        """
        Продление подписки.
        
        Args:
            subscription_id: ID подписки
            
        Returns:
            bool: True если продление успешно, False иначе
        """
        subscription = await self.get_subscription_by_id(subscription_id)
        if not subscription:
            return False
        
        # Вычисляем новые даты
        current_end = subscription.end_date or datetime.utcnow()
        if subscription.billing_cycle == "yearly":
            new_end = current_end + timedelta(days=365)
        else:  # monthly
            new_end = current_end + timedelta(days=30)
        
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(
                end_date=new_end,
                next_billing_date=new_end,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def get_expired_subscriptions(self) -> List[Subscription]:
        """
        Получение истекших подписок.
        
        Returns:
            List[Subscription]: Список истекших подписок
        """
        result = await self.db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.end_date < datetime.utcnow()
                )
            )
        )
        return result.scalars().all()
    
    async def expire_subscriptions(self) -> int:
        """
        Истечение подписок.
        
        Returns:
            int: Количество истекших подписок
        """
        expired_subscriptions = await self.get_expired_subscriptions()
        
        if not expired_subscriptions:
            return 0
        
        subscription_ids = [sub.id for sub in expired_subscriptions]
        
        await self.db.execute(
            update(Subscription)
            .where(Subscription.id.in_(subscription_ids))
            .values(
                status=SubscriptionStatus.EXPIRED,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return len(subscription_ids)
    
    async def get_plan_by_id(self, plan_id: int) -> Optional[Plan]:
        """
        Получение плана по ID.
        
        Args:
            plan_id: ID плана
            
        Returns:
            Optional[Plan]: План или None
        """
        result = await self.db.execute(
            select(Plan).where(Plan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    async def get_subscription_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получение статистики подписок пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Статистика подписок
        """
        # Общее количество подписок
        total_subscriptions_result = await self.db.execute(
            select(func.count(Subscription.id))
            .where(Subscription.user_id == user_id)
        )
        total_subscriptions = total_subscriptions_result.scalar() or 0
        
        # Активные подписки
        active_subscriptions_result = await self.db.execute(
            select(func.count(Subscription.id))
            .where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        active_subscriptions = active_subscriptions_result.scalar() or 0
        
        # Текущая подписка
        current_subscription = await self.get_active_subscription(user_id)
        
        return {
            "user_id": user_id,
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "current_subscription": current_subscription.to_dict() if current_subscription else None,
        }
