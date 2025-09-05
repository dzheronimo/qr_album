"""
Сервис для работы с уведомлениями.

Содержит бизнес-логику для отправки и управления уведомлениями.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.notification import (
    Notification, NotificationTemplate, NotificationType, 
    NotificationStatus, NotificationPriority
)


class NotificationService:
    """Сервис для работы с уведомлениями."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        content: str,
        subject: Optional[str] = None,
        template_id: Optional[int] = None,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        recipient_device_token: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Создание уведомления.
        
        Args:
            user_id: ID пользователя
            notification_type: Тип уведомления
            content: Содержимое уведомления
            subject: Тема (для email)
            template_id: ID шаблона
            recipient_email: Email получателя
            recipient_phone: Телефон получателя
            recipient_device_token: Токен устройства для push
            priority: Приоритет уведомления
            scheduled_at: Время отправки
            extra_data: Дополнительные данные
            
        Returns:
            Notification: Созданное уведомление
        """
        notification = Notification(
            user_id=user_id,
            template_id=template_id,
            notification_type=notification_type,
            subject=subject,
            content=content,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            recipient_device_token=recipient_device_token,
            priority=priority,
            scheduled_at=scheduled_at,
            extra_data=extra_data
        )
        
        try:
            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)
            return notification
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании уведомления")
    
    async def create_notification_from_template(
        self,
        user_id: int,
        template_name: str,
        variables: Dict[str, Any],
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
        recipient_device_token: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None
    ) -> Optional[Notification]:
        """
        Создание уведомления из шаблона.
        
        Args:
            user_id: ID пользователя
            template_name: Имя шаблона
            variables: Переменные для подстановки
            recipient_email: Email получателя
            recipient_phone: Телефон получателя
            recipient_device_token: Токен устройства для push
            priority: Приоритет уведомления
            scheduled_at: Время отправки
            
        Returns:
            Optional[Notification]: Созданное уведомление или None
        """
        # Получаем шаблон
        template_result = await self.db.execute(
            select(NotificationTemplate).where(NotificationTemplate.name == template_name)
        )
        template = template_result.scalar_one_or_none()
        
        if not template or not template.is_active:
            return None
        
        # Рендерим шаблон
        rendered = await self._render_template(template, variables)
        if not rendered:
            return None
        
        # Создаем уведомление
        return await self.create_notification(
            user_id=user_id,
            notification_type=template.notification_type,
            content=rendered["content"],
            subject=rendered["subject"],
            template_id=template.id,
            recipient_email=recipient_email,
            recipient_phone=recipient_phone,
            recipient_device_token=recipient_device_token,
            priority=priority,
            scheduled_at=scheduled_at
        )
    
    async def _render_template(
        self,
        template: NotificationTemplate,
        variables: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Рендеринг шаблона с переменными.
        
        Args:
            template: Шаблон уведомления
            variables: Переменные для подстановки
            
        Returns:
            Optional[Dict[str, str]]: Рендеренный контент или None
        """
        try:
            # Простая подстановка переменных
            content = template.content
            subject = template.subject or ""
            
            for key, value in variables.items():
                placeholder = f"{{{{{key}}}}}"
                content = content.replace(placeholder, str(value))
                subject = subject.replace(placeholder, str(value))
            
            return {
                "subject": subject,
                "content": content
            }
        except Exception:
            return None
    
    async def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        """
        Получение уведомления по ID.
        
        Args:
            notification_id: ID уведомления
            
        Returns:
            Optional[Notification]: Уведомление или None
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_notifications(
        self,
        user_id: int,
        notification_type: Optional[NotificationType] = None,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notification]:
        """
        Получение уведомлений пользователя.
        
        Args:
            user_id: ID пользователя
            notification_type: Тип уведомления для фильтрации
            status: Статус уведомления для фильтрации
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[Notification]: Список уведомлений
        """
        query = select(Notification).where(Notification.user_id == user_id)
        
        if notification_type:
            query = query.where(Notification.notification_type == notification_type)
        if status:
            query = query.where(Notification.status == status)
        
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_notification_status(
        self,
        notification_id: int,
        status: NotificationStatus,
        error_message: Optional[str] = None
    ) -> Optional[Notification]:
        """
        Обновление статуса уведомления.
        
        Args:
            notification_id: ID уведомления
            status: Новый статус
            error_message: Сообщение об ошибке
            
        Returns:
            Optional[Notification]: Обновленное уведомление или None
        """
        notification = await self.get_notification_by_id(notification_id)
        if not notification:
            return None
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == NotificationStatus.SENT:
            update_data["sent_at"] = datetime.utcnow()
        elif status == NotificationStatus.DELIVERED:
            update_data["delivered_at"] = datetime.utcnow()
        elif status == NotificationStatus.FAILED:
            update_data["error_message"] = error_message
        
        await self.db.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_notification_by_id(notification_id)
    
    async def send_notification(self, notification_id: int) -> bool:
        """
        Отправка уведомления (заглушка).
        
        Args:
            notification_id: ID уведомления
            
        Returns:
            bool: True если отправка успешна, False иначе
        """
        notification = await self.get_notification_by_id(notification_id)
        if not notification:
            return False
        
        try:
            # В реальном приложении здесь была бы интеграция с почтовыми сервисами,
            # push-уведомлениями, SMS-провайдерами и т.д.
            
            # Для демонстрации просто помечаем как отправленное
            await self.update_notification_status(
                notification_id=notification_id,
                status=NotificationStatus.SENT
            )
            
            # Имитируем доставку через некоторое время
            await self.update_notification_status(
                notification_id=notification_id,
                status=NotificationStatus.DELIVERED
            )
            
            return True
        except Exception as e:
            await self.update_notification_status(
                notification_id=notification_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )
            return False
    
    async def get_pending_notifications(
        self,
        limit: int = 100
    ) -> List[Notification]:
        """
        Получение уведомлений, ожидающих отправки.
        
        Args:
            limit: Лимит записей
            
        Returns:
            List[Notification]: Список уведомлений
        """
        now = datetime.utcnow()
        
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.status == NotificationStatus.PENDING,
                    or_(
                        Notification.scheduled_at.is_(None),
                        Notification.scheduled_at <= now
                    )
                )
            )
            .order_by(Notification.priority.desc(), Notification.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Получение статистики уведомлений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Статистика уведомлений
        """
        # Общее количество уведомлений
        total_notifications_result = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id)
        )
        total_notifications = total_notifications_result.scalar() or 0
        
        # Уведомления по статусам
        notifications_by_status_result = await self.db.execute(
            select(
                Notification.status,
                func.count(Notification.id).label('count')
            )
            .where(Notification.user_id == user_id)
            .group_by(Notification.status)
        )
        notifications_by_status = {row.status.value: row.count for row in notifications_by_status_result}
        
        # Уведомления по типам
        notifications_by_type_result = await self.db.execute(
            select(
                Notification.notification_type,
                func.count(Notification.id).label('count')
            )
            .where(Notification.user_id == user_id)
            .group_by(Notification.notification_type)
        )
        notifications_by_type = {row.notification_type.value: row.count for row in notifications_by_type_result}
        
        # Уведомления по приоритетам
        notifications_by_priority_result = await self.db.execute(
            select(
                Notification.priority,
                func.count(Notification.id).label('count')
            )
            .where(Notification.user_id == user_id)
            .group_by(Notification.priority)
        )
        notifications_by_priority = {row.priority.value: row.count for row in notifications_by_priority_result}
        
        return {
            "user_id": user_id,
            "total_notifications": total_notifications,
            "notifications_by_status": notifications_by_status,
            "notifications_by_type": notifications_by_type,
            "notifications_by_priority": notifications_by_priority
        }
