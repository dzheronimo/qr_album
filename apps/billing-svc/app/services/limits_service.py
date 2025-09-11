"""
Сервис для работы с лимитами пользователей.

Содержит бизнес-логику для получения и проверки лимитов в формате API.md.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.billing import Plan, Subscription, SubscriptionStatus, Usage
from app.models.limits import LimitsResponseV2, LimitInfo, StorageLimitInfo, create_limit_info, create_storage_limit_info


class LimitsService:
    """Сервис для работы с лимитами пользователей."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def get_user_limits(self, user_id: int) -> LimitsResponseV2:
        """
        Получение лимитов пользователя в формате API.md.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            LimitsResponseV2: Информация о лимитах пользователя
            
        Raises:
            ValueError: Если у пользователя нет активной подписки
        """
        # Получаем активную подписку пользователя
        subscription = await self._get_active_subscription(user_id)
        if not subscription:
            raise ValueError("У пользователя нет активной подписки")
        
        # Загружаем план
        plan = await self._get_plan(subscription.plan_id)
        if not plan:
            raise ValueError("План подписки не найден")
        
        # Получаем текущее использование
        current_usage = await self._get_current_usage(user_id)
        
        # Создаем информацию о лимитах
        albums_limit = create_limit_info(
            used=current_usage.albums_count if current_usage else 0,
            limit=plan.max_albums
        )
        
        pages_limit = create_limit_info(
            used=current_usage.pages_count if current_usage else 0,
            limit=plan.max_pages_per_album
        )
        
        storage_limit = create_storage_limit_info(
            used_mb=current_usage.storage_used_mb if current_usage else 0,
            limit_gb=plan.max_storage_gb
        )
        
        return LimitsResponseV2(
            albums=albums_limit,
            pages=pages_limit,
            storage=storage_limit
        )
    
    async def check_limits_for_operation(
        self,
        user_id: int,
        albums_delta: int = 0,
        pages_delta: int = 0,
        storage_delta_mb: int = 0
    ) -> Dict[str, Any]:
        """
        Проверяет, можно ли выполнить операцию с учетом лимитов.
        
        Args:
            user_id: ID пользователя
            albums_delta: Изменение количества альбомов
            pages_delta: Изменение количества страниц
            storage_delta_mb: Изменение хранилища в МБ
            
        Returns:
            Dict[str, Any]: Результат проверки
        """
        try:
            limits = await self.get_user_limits(user_id)
            
            # Проверяем каждый тип лимита
            can_proceed = True
            exceeded_limits = []
            
            # Проверка альбомов
            if albums_delta > 0 and not limits.albums.can_use(albums_delta):
                can_proceed = False
                exceeded_limits.append(f"Превышен лимит альбомов: {limits.albums.used + albums_delta}/{limits.albums.limit}")
            
            # Проверка страниц
            if pages_delta > 0 and not limits.pages.can_use(pages_delta):
                can_proceed = False
                exceeded_limits.append(f"Превышен лимит страниц: {limits.pages.used + pages_delta}/{limits.pages.limit}")
            
            # Проверка хранилища
            if storage_delta_mb > 0 and not limits.storage.can_use(storage_delta_mb):
                can_proceed = False
                exceeded_limits.append(f"Превышен лимит хранилища: {limits.storage.used_mb + storage_delta_mb}MB/{limits.storage.limit_mb}MB")
            
            return {
                "can_proceed": can_proceed,
                "exceeded_limits": exceeded_limits,
                "limits": limits.model_dump(),
                "message": None if can_proceed else "Превышены лимиты тарифного плана"
            }
            
        except ValueError as e:
            return {
                "can_proceed": False,
                "exceeded_limits": [],
                "limits": None,
                "message": str(e)
            }
    
    async def _get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """Получает активную подписку пользователя."""
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
    
    async def _get_plan(self, plan_id: int) -> Optional[Plan]:
        """Получает план по ID."""
        result = await self.db.execute(
            select(Plan).where(Plan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_current_usage(self, user_id: int) -> Optional[Usage]:
        """Получает текущее использование пользователя."""
        # Получаем текущий период (текущий месяц)
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        result = await self.db.execute(
            select(Usage)
            .where(
                and_(
                    Usage.user_id == user_id,
                    Usage.period_start == period_start,
                    Usage.period_end == period_end
                )
            )
        )
        return result.scalar_one_or_none()
