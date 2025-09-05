"""
Сервис для работы с тарифными планами.

Содержит бизнес-логику для управления тарифными планами.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.exc import IntegrityError

from app.models.billing import Plan, PlanType


class PlanService:
    """Сервис для работы с тарифными планами."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_plan(
        self,
        name: str,
        plan_type: PlanType,
        price_monthly: Decimal,
        price_yearly: Optional[Decimal] = None,
        currency: str = "USD",
        description: Optional[str] = None,
        max_albums: Optional[int] = None,
        max_pages_per_album: Optional[int] = None,
        max_media_files: Optional[int] = None,
        max_qr_codes: Optional[int] = None,
        max_storage_gb: Optional[int] = None,
        features: Optional[Dict[str, Any]] = None,
        is_popular: bool = False
    ) -> Plan:
        """
        Создание тарифного плана.
        
        Args:
            name: Название плана
            plan_type: Тип плана
            price_monthly: Месячная цена
            price_yearly: Годовая цена
            currency: Валюта
            description: Описание
            max_albums: Максимальное количество альбомов
            max_pages_per_album: Максимальное количество страниц в альбоме
            max_media_files: Максимальное количество медиафайлов
            max_qr_codes: Максимальное количество QR кодов
            max_storage_gb: Максимальное хранилище в ГБ
            features: Функции плана
            is_popular: Популярный план
            
        Returns:
            Plan: Созданный план
            
        Raises:
            ValueError: Если план с таким именем уже существует
        """
        plan = Plan(
            name=name,
            plan_type=plan_type,
            price_monthly=price_monthly,
            price_yearly=price_yearly,
            currency=currency,
            description=description,
            max_albums=max_albums,
            max_pages_per_album=max_pages_per_album,
            max_media_files=max_media_files,
            max_qr_codes=max_qr_codes,
            max_storage_gb=max_storage_gb,
            features=features,
            is_popular=is_popular
        )
        
        try:
            self.db.add(plan)
            await self.db.commit()
            await self.db.refresh(plan)
            return plan
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("План с таким именем уже существует")
    
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
    
    async def get_plan_by_name(self, name: str) -> Optional[Plan]:
        """
        Получение плана по имени.
        
        Args:
            name: Имя плана
            
        Returns:
            Optional[Plan]: План или None
        """
        result = await self.db.execute(
            select(Plan).where(Plan.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_plans(
        self,
        plan_type: Optional[PlanType] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[Plan]:
        """
        Получение списка планов.
        
        Args:
            plan_type: Тип плана для фильтрации
            is_active: Только активные планы
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[Plan]: Список планов
        """
        query = select(Plan)
        
        conditions = []
        if is_active:
            conditions.append(Plan.is_active == True)
        if plan_type:
            conditions.append(Plan.plan_type == plan_type)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Plan.price_monthly.asc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_popular_plans(self) -> List[Plan]:
        """
        Получение популярных планов.
        
        Returns:
            List[Plan]: Список популярных планов
        """
        result = await self.db.execute(
            select(Plan)
            .where(and_(Plan.is_active == True, Plan.is_popular == True))
            .order_by(Plan.price_monthly.asc())
        )
        return result.scalars().all()
    
    async def update_plan(
        self,
        plan_id: int,
        name: Optional[str] = None,
        plan_type: Optional[PlanType] = None,
        price_monthly: Optional[Decimal] = None,
        price_yearly: Optional[Decimal] = None,
        currency: Optional[str] = None,
        description: Optional[str] = None,
        max_albums: Optional[int] = None,
        max_pages_per_album: Optional[int] = None,
        max_media_files: Optional[int] = None,
        max_qr_codes: Optional[int] = None,
        max_storage_gb: Optional[int] = None,
        features: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        is_popular: Optional[bool] = None
    ) -> Optional[Plan]:
        """
        Обновление тарифного плана.
        
        Args:
            plan_id: ID плана
            name: Название плана
            plan_type: Тип плана
            price_monthly: Месячная цена
            price_yearly: Годовая цена
            currency: Валюта
            description: Описание
            max_albums: Максимальное количество альбомов
            max_pages_per_album: Максимальное количество страниц в альбоме
            max_media_files: Максимальное количество медиафайлов
            max_qr_codes: Максимальное количество QR кодов
            max_storage_gb: Максимальное хранилище в ГБ
            features: Функции плана
            is_active: Активный план
            is_popular: Популярный план
            
        Returns:
            Optional[Plan]: Обновленный план или None
        """
        plan = await self.get_plan_by_id(plan_id)
        if not plan:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if plan_type is not None:
            update_data["plan_type"] = plan_type
        if price_monthly is not None:
            update_data["price_monthly"] = price_monthly
        if price_yearly is not None:
            update_data["price_yearly"] = price_yearly
        if currency is not None:
            update_data["currency"] = currency
        if description is not None:
            update_data["description"] = description
        if max_albums is not None:
            update_data["max_albums"] = max_albums
        if max_pages_per_album is not None:
            update_data["max_pages_per_album"] = max_pages_per_album
        if max_media_files is not None:
            update_data["max_media_files"] = max_media_files
        if max_qr_codes is not None:
            update_data["max_qr_codes"] = max_qr_codes
        if max_storage_gb is not None:
            update_data["max_storage_gb"] = max_storage_gb
        if features is not None:
            update_data["features"] = features
        if is_active is not None:
            update_data["is_active"] = is_active
        if is_popular is not None:
            update_data["is_popular"] = is_popular
        
        if not update_data:
            return plan
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await self.db.execute(
                update(Plan)
                .where(Plan.id == plan_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_plan_by_id(plan_id)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("План с таким именем уже существует")
    
    async def delete_plan(self, plan_id: int) -> bool:
        """
        Удаление тарифного плана.
        
        Args:
            plan_id: ID плана
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        plan = await self.get_plan_by_id(plan_id)
        if not plan:
            return False
        
        # Проверяем, есть ли активные подписки на этот план
        from app.models.billing import Subscription, SubscriptionStatus
        active_subscriptions_result = await self.db.execute(
            select(Subscription.id)
            .where(
                and_(
                    Subscription.plan_id == plan_id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
            .limit(1)
        )
        
        if active_subscriptions_result.scalar_one_or_none():
            raise ValueError("Нельзя удалить план с активными подписками")
        
        await self.db.execute(
            delete(Plan).where(Plan.id == plan_id)
        )
        await self.db.commit()
        
        return True
    
    async def deactivate_plan(self, plan_id: int) -> bool:
        """
        Деактивация тарифного плана.
        
        Args:
            plan_id: ID плана
            
        Returns:
            bool: True если деактивация успешна, False иначе
        """
        plan = await self.get_plan_by_id(plan_id)
        if not plan:
            return False
        
        await self.db.execute(
            update(Plan)
            .where(Plan.id == plan_id)
            .values(
                is_active=False,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def get_plan_stats(self) -> Dict[str, Any]:
        """
        Получение статистики планов.
        
        Returns:
            Dict[str, Any]: Статистика планов
        """
        from sqlalchemy import func
        from app.models.billing import Subscription, SubscriptionStatus
        
        # Общее количество планов
        total_plans_result = await self.db.execute(
            select(func.count(Plan.id))
        )
        total_plans = total_plans_result.scalar() or 0
        
        # Активные планы
        active_plans_result = await self.db.execute(
            select(func.count(Plan.id))
            .where(Plan.is_active == True)
        )
        active_plans = active_plans_result.scalar() or 0
        
        # Популярные планы
        popular_plans_result = await self.db.execute(
            select(func.count(Plan.id))
            .where(and_(Plan.is_active == True, Plan.is_popular == True))
        )
        popular_plans = popular_plans_result.scalar() or 0
        
        # Планы по типам
        plans_by_type_result = await self.db.execute(
            select(
                Plan.plan_type,
                func.count(Plan.id).label('count')
            )
            .where(Plan.is_active == True)
            .group_by(Plan.plan_type)
        )
        plans_by_type = {row.plan_type.value: row.count for row in plans_by_type_result}
        
        # Планы с активными подписками
        plans_with_subscriptions_result = await self.db.execute(
            select(
                Plan.id,
                Plan.name,
                func.count(Subscription.id).label('subscriptions_count')
            )
            .join(Subscription, Plan.id == Subscription.plan_id)
            .where(Subscription.status == SubscriptionStatus.ACTIVE)
            .group_by(Plan.id, Plan.name)
            .order_by(func.count(Subscription.id).desc())
            .limit(10)
        )
        plans_with_subscriptions = [
            {
                "plan_id": row.id,
                "plan_name": row.name,
                "subscriptions_count": row.subscriptions_count
            }
            for row in plans_with_subscriptions_result
        ]
        
        return {
            "total_plans": total_plans,
            "active_plans": active_plans,
            "popular_plans": popular_plans,
            "plans_by_type": plans_by_type,
            "top_plans_by_subscriptions": plans_with_subscriptions
        }
