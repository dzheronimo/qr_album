"""
Сервис для работы с шаблонами уведомлений.

Содержит бизнес-логику для управления шаблонами уведомлений.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.exc import IntegrityError

from app.models.notification import NotificationTemplate, NotificationType


class TemplateService:
    """Сервис для работы с шаблонами уведомлений."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_template(
        self,
        name: str,
        notification_type: NotificationType,
        content: str,
        subject: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        category: Optional[str] = None
    ) -> NotificationTemplate:
        """
        Создание шаблона уведомления.
        
        Args:
            name: Название шаблона
            notification_type: Тип уведомления
            content: Содержимое шаблона
            subject: Тема (для email)
            variables: Переменные для подстановки
            description: Описание шаблона
            category: Категория шаблона
            
        Returns:
            NotificationTemplate: Созданный шаблон
            
        Raises:
            ValueError: Если шаблон с таким именем уже существует
        """
        template = NotificationTemplate(
            name=name,
            notification_type=notification_type,
            content=content,
            subject=subject,
            variables=variables,
            description=description,
            category=category
        )
        
        try:
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)
            return template
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Шаблон с таким именем уже существует")
    
    async def get_template_by_id(self, template_id: int) -> Optional[NotificationTemplate]:
        """
        Получение шаблона по ID.
        
        Args:
            template_id: ID шаблона
            
        Returns:
            Optional[NotificationTemplate]: Шаблон или None
        """
        result = await self.db.execute(
            select(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def get_template_by_name(self, name: str) -> Optional[NotificationTemplate]:
        """
        Получение шаблона по имени.
        
        Args:
            name: Имя шаблона
            
        Returns:
            Optional[NotificationTemplate]: Шаблон или None
        """
        result = await self.db.execute(
            select(NotificationTemplate).where(NotificationTemplate.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_templates(
        self,
        notification_type: Optional[NotificationType] = None,
        category: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 50
    ) -> List[NotificationTemplate]:
        """
        Получение списка шаблонов.
        
        Args:
            notification_type: Тип уведомления для фильтрации
            category: Категория для фильтрации
            is_active: Только активные шаблоны
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[NotificationTemplate]: Список шаблонов
        """
        query = select(NotificationTemplate)
        
        conditions = []
        if is_active:
            conditions.append(NotificationTemplate.is_active == True)
        if notification_type:
            conditions.append(NotificationTemplate.notification_type == notification_type)
        if category:
            conditions.append(NotificationTemplate.category == category)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(NotificationTemplate.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        notification_type: Optional[NotificationType] = None,
        content: Optional[str] = None,
        subject: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[NotificationTemplate]:
        """
        Обновление шаблона уведомления.
        
        Args:
            template_id: ID шаблона
            name: Название шаблона
            notification_type: Тип уведомления
            content: Содержимое шаблона
            subject: Тема (для email)
            variables: Переменные для подстановки
            description: Описание шаблона
            category: Категория шаблона
            is_active: Активный шаблон
            
        Returns:
            Optional[NotificationTemplate]: Обновленный шаблон или None
        """
        template = await self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if notification_type is not None:
            update_data["notification_type"] = notification_type
        if content is not None:
            update_data["content"] = content
        if subject is not None:
            update_data["subject"] = subject
        if variables is not None:
            update_data["variables"] = variables
        if description is not None:
            update_data["description"] = description
        if category is not None:
            update_data["category"] = category
        if is_active is not None:
            update_data["is_active"] = is_active
        
        if not update_data:
            return template
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await self.db.execute(
                update(NotificationTemplate)
                .where(NotificationTemplate.id == template_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_template_by_id(template_id)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Шаблон с таким именем уже существует")
    
    async def delete_template(self, template_id: int) -> bool:
        """
        Удаление шаблона уведомления.
        
        Args:
            template_id: ID шаблона
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        template = await self.get_template_by_id(template_id)
        if not template:
            return False
        
        # Проверяем, есть ли уведомления, использующие этот шаблон
        from app.models.notification import Notification
        notifications_result = await self.db.execute(
            select(Notification.id)
            .where(Notification.template_id == template_id)
            .limit(1)
        )
        
        if notifications_result.scalar_one_or_none():
            raise ValueError("Нельзя удалить шаблон, который используется в уведомлениях")
        
        await self.db.execute(
            delete(NotificationTemplate).where(NotificationTemplate.id == template_id)
        )
        await self.db.commit()
        
        return True
    
    async def render_template(
        self,
        template_id: int,
        variables: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Рендеринг шаблона с переменными.
        
        Args:
            template_id: ID шаблона
            variables: Переменные для подстановки
            
        Returns:
            Optional[Dict[str, str]]: Рендеренный контент или None
        """
        template = await self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Простая подстановка переменных (в реальном проекте можно использовать Jinja2)
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
    
    async def get_template_stats(self) -> Dict[str, Any]:
        """
        Получение статистики шаблонов.
        
        Returns:
            Dict[str, Any]: Статистика шаблонов
        """
        from sqlalchemy import func
        from app.models.notification import Notification
        
        # Общее количество шаблонов
        total_templates_result = await self.db.execute(
            select(func.count(NotificationTemplate.id))
        )
        total_templates = total_templates_result.scalar() or 0
        
        # Активные шаблоны
        active_templates_result = await self.db.execute(
            select(func.count(NotificationTemplate.id))
            .where(NotificationTemplate.is_active == True)
        )
        active_templates = active_templates_result.scalar() or 0
        
        # Шаблоны по типам
        templates_by_type_result = await self.db.execute(
            select(
                NotificationTemplate.notification_type,
                func.count(NotificationTemplate.id).label('count')
            )
            .where(NotificationTemplate.is_active == True)
            .group_by(NotificationTemplate.notification_type)
        )
        templates_by_type = {row.notification_type.value: row.count for row in templates_by_type_result}
        
        # Шаблоны с уведомлениями
        templates_with_notifications_result = await self.db.execute(
            select(
                NotificationTemplate.id,
                NotificationTemplate.name,
                func.count(Notification.id).label('notifications_count')
            )
            .join(Notification, NotificationTemplate.id == Notification.template_id)
            .group_by(NotificationTemplate.id, NotificationTemplate.name)
            .order_by(func.count(Notification.id).desc())
            .limit(10)
        )
        templates_with_notifications = [
            {
                "template_id": row.id,
                "template_name": row.name,
                "notifications_count": row.notifications_count
            }
            for row in templates_with_notifications_result
        ]
        
        return {
            "total_templates": total_templates,
            "active_templates": active_templates,
            "templates_by_type": templates_by_type,
            "top_templates_by_usage": templates_with_notifications
        }
