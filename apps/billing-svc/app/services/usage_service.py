"""
Сервис для работы с использованием ресурсов.

Содержит бизнес-логику для отслеживания использования ресурсов пользователями.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.models.billing import Usage, Plan, Subscription, SubscriptionStatus


class UsageService:
    """Сервис для работы с использованием ресурсов."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def get_current_usage(self, user_id: int) -> Optional[Usage]:
        """
        Получение текущего использования ресурсов пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Usage]: Текущее использование или None
        """
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
    
    async def create_or_update_usage(
        self,
        user_id: int,
        albums_count: Optional[int] = None,
        pages_count: Optional[int] = None,
        media_files_count: Optional[int] = None,
        qr_codes_count: Optional[int] = None,
        storage_used_mb: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Usage:
        """
        Создание или обновление использования ресурсов.
        
        Args:
            user_id: ID пользователя
            albums_count: Количество альбомов
            pages_count: Количество страниц
            media_files_count: Количество медиафайлов
            qr_codes_count: Количество QR кодов
            storage_used_mb: Использованное хранилище в МБ
            extra_data: Дополнительные данные
            
        Returns:
            Usage: Обновленное использование
        """
        # Получаем текущий период
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Проверяем, есть ли уже запись для этого периода
        current_usage = await self.get_current_usage(user_id)
        
        if current_usage:
            # Обновляем существующую запись
            update_data = {}
            
            if albums_count is not None:
                update_data["albums_count"] = albums_count
            if pages_count is not None:
                update_data["pages_count"] = pages_count
            if media_files_count is not None:
                update_data["media_files_count"] = media_files_count
            if qr_codes_count is not None:
                update_data["qr_codes_count"] = qr_codes_count
            if storage_used_mb is not None:
                update_data["storage_used_mb"] = storage_used_mb
            if extra_data is not None:
                update_data["extra_data"] = extra_data
            
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                
                await self.db.execute(
                    update(Usage)
                    .where(Usage.id == current_usage.id)
                    .values(**update_data)
                )
                await self.db.commit()
                
                return await self.get_current_usage(user_id)
            else:
                return current_usage
        else:
            # Создаем новую запись
            usage = Usage(
                user_id=user_id,
                albums_count=albums_count or 0,
                pages_count=pages_count or 0,
                media_files_count=media_files_count or 0,
                qr_codes_count=qr_codes_count or 0,
                storage_used_mb=storage_used_mb or 0,
                period_start=period_start,
                period_end=period_end,
                extra_data=extra_data
            )
            
            try:
                self.db.add(usage)
                await self.db.commit()
                await self.db.refresh(usage)
                return usage
            except IntegrityError:
                await self.db.rollback()
                raise ValueError("Ошибка при создании записи использования")
    
    async def increment_usage(
        self,
        user_id: int,
        albums_count: int = 0,
        pages_count: int = 0,
        media_files_count: int = 0,
        qr_codes_count: int = 0,
        storage_used_mb: int = 0
    ) -> Usage:
        """
        Увеличение использования ресурсов.
        
        Args:
            user_id: ID пользователя
            albums_count: Увеличение количества альбомов
            pages_count: Увеличение количества страниц
            media_files_count: Увеличение количества медиафайлов
            qr_codes_count: Увеличение количества QR кодов
            storage_used_mb: Увеличение используемого хранилища в МБ
            
        Returns:
            Usage: Обновленное использование
        """
        current_usage = await self.get_current_usage(user_id)
        
        if current_usage:
            return await self.create_or_update_usage(
                user_id=user_id,
                albums_count=current_usage.albums_count + albums_count,
                pages_count=current_usage.pages_count + pages_count,
                media_files_count=current_usage.media_files_count + media_files_count,
                qr_codes_count=current_usage.qr_codes_count + qr_codes_count,
                storage_used_mb=current_usage.storage_used_mb + storage_used_mb
            )
        else:
            return await self.create_or_update_usage(
                user_id=user_id,
                albums_count=albums_count,
                pages_count=pages_count,
                media_files_count=media_files_count,
                qr_codes_count=qr_codes_count,
                storage_used_mb=storage_used_mb
            )
    
    async def check_limits(
        self,
        user_id: int,
        albums_count: Optional[int] = None,
        pages_count: Optional[int] = None,
        media_files_count: Optional[int] = None,
        qr_codes_count: Optional[int] = None,
        storage_used_mb: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Проверка лимитов пользователя.
        
        Args:
            user_id: ID пользователя
            albums_count: Количество альбомов для проверки
            pages_count: Количество страниц для проверки
            media_files_count: Количество медиафайлов для проверки
            qr_codes_count: Количество QR кодов для проверки
            storage_used_mb: Использованное хранилище в МБ для проверки
            
        Returns:
            Dict[str, Any]: Результат проверки лимитов
        """
        # Получаем активную подписку пользователя
        subscription_result = await self.db.execute(
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
        subscription = subscription_result.scalar_one_or_none()
        
        if not subscription:
            return {
                "has_subscription": False,
                "plan": None,
                "current_usage": None,
                "limits_exceeded": True,
                "exceeded_limits": [],
                "can_proceed": False,
                "message": "У пользователя нет активной подписки"
            }
        
        # Загружаем план отдельно
        plan_result = await self.db.execute(
            select(Plan).where(Plan.id == subscription.plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        
        if not plan:
            return {
                "has_subscription": False,
                "plan": None,
                "current_usage": None,
                "limits_exceeded": True,
                "exceeded_limits": [],
                "can_proceed": False,
                "message": "План подписки не найден"
            }
        
        current_usage = await self.get_current_usage(user_id)
        
        # Проверяем лимиты
        limits_exceeded = []
        
        if albums_count is not None and plan.max_albums is not None:
            current_albums = (current_usage.albums_count if current_usage else 0) + albums_count
            if current_albums > plan.max_albums:
                limits_exceeded.append(f"Превышен лимит альбомов: {current_albums}/{plan.max_albums}")
        
        if pages_count is not None and plan.max_pages_per_album is not None:
            current_pages = (current_usage.pages_count if current_usage else 0) + pages_count
            if current_pages > plan.max_pages_per_album:
                limits_exceeded.append(f"Превышен лимит страниц: {current_pages}/{plan.max_pages_per_album}")
        
        if media_files_count is not None and plan.max_media_files is not None:
            current_media = (current_usage.media_files_count if current_usage else 0) + media_files_count
            if current_media > plan.max_media_files:
                limits_exceeded.append(f"Превышен лимит медиафайлов: {current_media}/{plan.max_media_files}")
        
        if qr_codes_count is not None and plan.max_qr_codes is not None:
            current_qr = (current_usage.qr_codes_count if current_usage else 0) + qr_codes_count
            if current_qr > plan.max_qr_codes:
                limits_exceeded.append(f"Превышен лимит QR кодов: {current_qr}/{plan.max_qr_codes}")
        
        if storage_used_mb is not None and plan.max_storage_gb is not None:
            current_storage = (current_usage.storage_used_mb if current_usage else 0) + storage_used_mb
            max_storage_mb = plan.max_storage_gb * 1024
            if current_storage > max_storage_mb:
                limits_exceeded.append(f"Превышен лимит хранилища: {current_storage/1024:.2f}GB/{plan.max_storage_gb}GB")
        
        return {
            "has_subscription": True,
            "plan": plan.to_dict(),
            "current_usage": current_usage.to_dict() if current_usage else None,
            "limits_exceeded": len(limits_exceeded) > 0,
            "exceeded_limits": limits_exceeded,
            "can_proceed": len(limits_exceeded) == 0,
            "message": None
        }
    
    async def get_usage_history(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 12
    ) -> List[Usage]:
        """
        Получение истории использования ресурсов.
        
        Args:
            user_id: ID пользователя
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[Usage]: История использования
        """
        result = await self.db.execute(
            select(Usage)
            .where(Usage.user_id == user_id)
            .order_by(Usage.period_start.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_usage_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получение статистики использования ресурсов.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Статистика использования
        """
        current_usage = await self.get_current_usage(user_id)
        
        # Получаем активную подписку
        subscription_result = await self.db.execute(
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
        subscription = subscription_result.scalar_one_or_none()
        
        if not subscription:
            return {
                "user_id": user_id,
                "has_subscription": False,
                "current_usage": None,
                "limits": None,
                "usage_percentages": None
            }
        
        # Загружаем план отдельно
        plan_result = await self.db.execute(
            select(Plan).where(Plan.id == subscription.plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        
        if not plan:
            return {
                "user_id": user_id,
                "has_subscription": False,
                "current_usage": None,
                "limits": None,
                "usage_percentages": None
            }
        
        # Вычисляем проценты использования
        usage_percentages = {}
        
        if plan.max_albums:
            usage_percentages["albums"] = min(100, (current_usage.albums_count / plan.max_albums) * 100) if current_usage else 0
        
        if plan.max_pages_per_album:
            usage_percentages["pages"] = min(100, (current_usage.pages_count / plan.max_pages_per_album) * 100) if current_usage else 0
        
        if plan.max_media_files:
            usage_percentages["media_files"] = min(100, (current_usage.media_files_count / plan.max_media_files) * 100) if current_usage else 0
        
        if plan.max_qr_codes:
            usage_percentages["qr_codes"] = min(100, (current_usage.qr_codes_count / plan.max_qr_codes) * 100) if current_usage else 0
        
        if plan.max_storage_gb:
            max_storage_mb = plan.max_storage_gb * 1024
            usage_percentages["storage"] = min(100, (current_usage.storage_used_mb / max_storage_mb) * 100) if current_usage else 0
        
        return {
            "user_id": user_id,
            "has_subscription": True,
            "plan": plan.to_dict(),
            "current_usage": current_usage.to_dict() if current_usage else None,
            "limits": {
                "max_albums": plan.max_albums,
                "max_pages_per_album": plan.max_pages_per_album,
                "max_media_files": plan.max_media_files,
                "max_qr_codes": plan.max_qr_codes,
                "max_storage_gb": plan.max_storage_gb
            },
            "usage_percentages": usage_percentages
        }
