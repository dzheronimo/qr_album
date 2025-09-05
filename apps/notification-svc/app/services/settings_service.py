"""
Сервис для работы с настройками уведомлений.

Содержит бизнес-логику для управления настройками уведомлений пользователей.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from app.models.notification import NotificationSettings


class SettingsService:
    """Сервис для работы с настройками уведомлений."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def get_user_settings(self, user_id: int) -> Optional[NotificationSettings]:
        """
        Получение настроек уведомлений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[NotificationSettings]: Настройки или None
        """
        result = await self.db.execute(
            select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user_settings(
        self,
        user_id: int,
        email_enabled: bool = True,
        push_enabled: bool = True,
        sms_enabled: bool = False,
        in_app_enabled: bool = True,
        marketing_emails: bool = False,
        system_notifications: bool = True,
        security_alerts: bool = True,
        billing_notifications: bool = True,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None,
        timezone: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> NotificationSettings:
        """
        Создание настроек уведомлений для пользователя.
        
        Args:
            user_id: ID пользователя
            email_enabled: Включены ли email уведомления
            push_enabled: Включены ли push уведомления
            sms_enabled: Включены ли SMS уведомления
            in_app_enabled: Включены ли внутриприложенные уведомления
            marketing_emails: Включены ли маркетинговые письма
            system_notifications: Включены ли системные уведомления
            security_alerts: Включены ли уведомления безопасности
            billing_notifications: Включены ли уведомления о биллинге
            quiet_hours_start: Начало тихих часов (HH:MM)
            quiet_hours_end: Конец тихих часов (HH:MM)
            timezone: Часовой пояс
            extra_data: Дополнительные данные
            
        Returns:
            NotificationSettings: Созданные настройки
        """
        settings = NotificationSettings(
            user_id=user_id,
            email_enabled=email_enabled,
            push_enabled=push_enabled,
            sms_enabled=sms_enabled,
            in_app_enabled=in_app_enabled,
            marketing_emails=marketing_emails,
            system_notifications=system_notifications,
            security_alerts=security_alerts,
            billing_notifications=billing_notifications,
            quiet_hours_start=quiet_hours_start,
            quiet_hours_end=quiet_hours_end,
            timezone=timezone,
            extra_data=extra_data
        )
        
        try:
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
            return settings
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Настройки для этого пользователя уже существуют")
    
    async def update_user_settings(
        self,
        user_id: int,
        email_enabled: Optional[bool] = None,
        push_enabled: Optional[bool] = None,
        sms_enabled: Optional[bool] = None,
        in_app_enabled: Optional[bool] = None,
        marketing_emails: Optional[bool] = None,
        system_notifications: Optional[bool] = None,
        security_alerts: Optional[bool] = None,
        billing_notifications: Optional[bool] = None,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None,
        timezone: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[NotificationSettings]:
        """
        Обновление настроек уведомлений пользователя.
        
        Args:
            user_id: ID пользователя
            email_enabled: Включены ли email уведомления
            push_enabled: Включены ли push уведомления
            sms_enabled: Включены ли SMS уведомления
            in_app_enabled: Включены ли внутриприложенные уведомления
            marketing_emails: Включены ли маркетинговые письма
            system_notifications: Включены ли системные уведомления
            security_alerts: Включены ли уведомления безопасности
            billing_notifications: Включены ли уведомления о биллинге
            quiet_hours_start: Начало тихих часов (HH:MM)
            quiet_hours_end: Конец тихих часов (HH:MM)
            timezone: Часовой пояс
            extra_data: Дополнительные данные
            
        Returns:
            Optional[NotificationSettings]: Обновленные настройки или None
        """
        settings = await self.get_user_settings(user_id)
        if not settings:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if email_enabled is not None:
            update_data["email_enabled"] = email_enabled
        if push_enabled is not None:
            update_data["push_enabled"] = push_enabled
        if sms_enabled is not None:
            update_data["sms_enabled"] = sms_enabled
        if in_app_enabled is not None:
            update_data["in_app_enabled"] = in_app_enabled
        if marketing_emails is not None:
            update_data["marketing_emails"] = marketing_emails
        if system_notifications is not None:
            update_data["system_notifications"] = system_notifications
        if security_alerts is not None:
            update_data["security_alerts"] = security_alerts
        if billing_notifications is not None:
            update_data["billing_notifications"] = billing_notifications
        if quiet_hours_start is not None:
            update_data["quiet_hours_start"] = quiet_hours_start
        if quiet_hours_end is not None:
            update_data["quiet_hours_end"] = quiet_hours_end
        if timezone is not None:
            update_data["timezone"] = timezone
        if extra_data is not None:
            update_data["extra_data"] = extra_data
        
        if not update_data:
            return settings
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(NotificationSettings)
            .where(NotificationSettings.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_user_settings(user_id)
    
    async def delete_user_settings(self, user_id: int) -> bool:
        """
        Удаление настроек уведомлений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        settings = await self.get_user_settings(user_id)
        if not settings:
            return False
        
        await self.db.execute(
            delete(NotificationSettings).where(NotificationSettings.user_id == user_id)
        )
        await self.db.commit()
        
        return True
    
    async def reset_user_settings(self, user_id: int) -> Optional[NotificationSettings]:
        """
        Сброс настроек уведомлений пользователя к значениям по умолчанию.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[NotificationSettings]: Сброшенные настройки или None
        """
        settings = await self.get_user_settings(user_id)
        if not settings:
            return None
        
        # Сбрасываем к значениям по умолчанию
        await self.update_user_settings(
            user_id=user_id,
            email_enabled=True,
            push_enabled=True,
            sms_enabled=False,
            in_app_enabled=True,
            marketing_emails=False,
            system_notifications=True,
            security_alerts=True,
            billing_notifications=True,
            quiet_hours_start=None,
            quiet_hours_end=None,
            timezone=None,
            extra_data=None
        )
        
        return await self.get_user_settings(user_id)
    
    async def can_send_notification(
        self,
        user_id: int,
        notification_type: str,
        category: Optional[str] = None
    ) -> bool:
        """
        Проверка, можно ли отправить уведомление пользователю.
        
        Args:
            user_id: ID пользователя
            notification_type: Тип уведомления
            category: Категория уведомления
            
        Returns:
            bool: True если можно отправить, False иначе
        """
        settings = await self.get_user_settings(user_id)
        if not settings:
            # Если настроек нет, используем значения по умолчанию
            return True
        
        # Проверяем тип уведомления
        if notification_type == "email" and not settings.email_enabled:
            return False
        elif notification_type == "push" and not settings.push_enabled:
            return False
        elif notification_type == "sms" and not settings.sms_enabled:
            return False
        elif notification_type == "in_app" and not settings.in_app_enabled:
            return False
        
        # Проверяем категорию
        if category == "marketing" and not settings.marketing_emails:
            return False
        elif category == "system" and not settings.system_notifications:
            return False
        elif category == "security" and not settings.security_alerts:
            return False
        elif category == "billing" and not settings.billing_notifications:
            return False
        
        # Проверяем тихие часы (упрощенная проверка)
        if settings.quiet_hours_start and settings.quiet_hours_end:
            # В реальном приложении здесь была бы проверка текущего времени
            # с учетом часового пояса пользователя
            pass
        
        return True
    
    async def get_settings_stats(self) -> Dict[str, Any]:
        """
        Получение статистики настроек уведомлений.
        
        Returns:
            Dict[str, Any]: Статистика настроек
        """
        from sqlalchemy import func
        
        # Общее количество пользователей с настройками
        total_users_result = await self.db.execute(
            select(func.count(NotificationSettings.id))
        )
        total_users = total_users_result.scalar() or 0
        
        # Статистика по типам уведомлений
        email_enabled_result = await self.db.execute(
            select(func.count(NotificationSettings.id))
            .where(NotificationSettings.email_enabled == True)
        )
        email_enabled = email_enabled_result.scalar() or 0
        
        push_enabled_result = await self.db.execute(
            select(func.count(NotificationSettings.id))
            .where(NotificationSettings.push_enabled == True)
        )
        push_enabled = push_enabled_result.scalar() or 0
        
        sms_enabled_result = await self.db.execute(
            select(func.count(NotificationSettings.id))
            .where(NotificationSettings.sms_enabled == True)
        )
        sms_enabled = sms_enabled_result.scalar() or 0
        
        # Статистика по категориям
        marketing_enabled_result = await self.db.execute(
            select(func.count(NotificationSettings.id))
            .where(NotificationSettings.marketing_emails == True)
        )
        marketing_enabled = marketing_enabled_result.scalar() or 0
        
        return {
            "total_users_with_settings": total_users,
            "email_enabled": email_enabled,
            "push_enabled": push_enabled,
            "sms_enabled": sms_enabled,
            "marketing_enabled": marketing_enabled
        }
