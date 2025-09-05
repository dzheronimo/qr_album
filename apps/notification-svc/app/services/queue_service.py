"""
Сервис для работы с очередью уведомлений.

Содержит бизнес-логику для управления очередью отправки уведомлений.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.notification import (
    NotificationQueue, Notification, NotificationPriority, 
    NotificationStatus
)


class QueueService:
    """Сервис для работы с очередью уведомлений."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def add_to_queue(
        self,
        notification_id: int,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        max_attempts: int = 3,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> NotificationQueue:
        """
        Добавление уведомления в очередь.
        
        Args:
            notification_id: ID уведомления
            priority: Приоритет уведомления
            scheduled_at: Время отправки
            max_attempts: Максимальное количество попыток
            extra_data: Дополнительные данные
            
        Returns:
            NotificationQueue: Элемент очереди
        """
        if scheduled_at is None:
            scheduled_at = datetime.utcnow()
        
        queue_item = NotificationQueue(
            notification_id=notification_id,
            priority=priority,
            scheduled_at=scheduled_at,
            max_attempts=max_attempts,
            extra_data=extra_data
        )
        
        try:
            self.db.add(queue_item)
            await self.db.commit()
            await self.db.refresh(queue_item)
            return queue_item
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при добавлении в очередь")
    
    async def get_queue_item_by_id(self, queue_id: int) -> Optional[NotificationQueue]:
        """
        Получение элемента очереди по ID.
        
        Args:
            queue_id: ID элемента очереди
            
        Returns:
            Optional[NotificationQueue]: Элемент очереди или None
        """
        result = await self.db.execute(
            select(NotificationQueue).where(NotificationQueue.id == queue_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_queue_items(
        self,
        limit: int = 100
    ) -> List[NotificationQueue]:
        """
        Получение элементов очереди, готовых к обработке.
        
        Args:
            limit: Лимит записей
            
        Returns:
            List[NotificationQueue]: Список элементов очереди
        """
        now = datetime.utcnow()
        
        result = await self.db.execute(
            select(NotificationQueue)
            .where(
                and_(
                    NotificationQueue.scheduled_at <= now,
                    NotificationQueue.is_processing == False,
                    NotificationQueue.attempts < NotificationQueue.max_attempts
                )
            )
            .order_by(
                NotificationQueue.priority.desc(),
                NotificationQueue.scheduled_at.asc()
            )
            .limit(limit)
        )
        return result.scalars().all()
    
    async def mark_as_processing(self, queue_id: int) -> bool:
        """
        Отметка элемента очереди как обрабатываемого.
        
        Args:
            queue_id: ID элемента очереди
            
        Returns:
            bool: True если успешно, False иначе
        """
        queue_item = await self.get_queue_item_by_id(queue_id)
        if not queue_item:
            return False
        
        await self.db.execute(
            update(NotificationQueue)
            .where(NotificationQueue.id == queue_id)
            .values(
                is_processing=True,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def mark_as_processed(
        self,
        queue_id: int,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Отметка элемента очереди как обработанного.
        
        Args:
            queue_id: ID элемента очереди
            success: Успешность обработки
            error_message: Сообщение об ошибке
            
        Returns:
            bool: True если успешно, False иначе
        """
        queue_item = await self.get_queue_item_by_id(queue_id)
        if not queue_item:
            return False
        
        # Обновляем счетчик попыток
        new_attempts = queue_item.attempts + 1
        
        if success:
            # Успешная обработка - удаляем из очереди
            await self.db.execute(
                delete(NotificationQueue).where(NotificationQueue.id == queue_id)
            )
        else:
            # Неуспешная обработка - обновляем попытки
            if new_attempts >= queue_item.max_attempts:
                # Превышено максимальное количество попыток
                await self.db.execute(
                    update(NotificationQueue)
                    .where(NotificationQueue.id == queue_id)
                    .values(
                        is_processing=False,
                        attempts=new_attempts,
                        processed_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                )
                
                # Обновляем статус уведомления
                await self.db.execute(
                    update(Notification)
                    .where(Notification.id == queue_item.notification_id)
                    .values(
                        status=NotificationStatus.FAILED,
                        error_message=error_message,
                        updated_at=datetime.utcnow()
                    )
                )
            else:
                # Планируем повторную попытку
                retry_delay = min(300 * (2 ** new_attempts), 3600)  # Экспоненциальная задержка
                retry_at = datetime.utcnow() + timedelta(seconds=retry_delay)
                
                await self.db.execute(
                    update(NotificationQueue)
                    .where(NotificationQueue.id == queue_id)
                    .values(
                        is_processing=False,
                        attempts=new_attempts,
                        scheduled_at=retry_at,
                        updated_at=datetime.utcnow()
                    )
                )
        
        await self.db.commit()
        return True
    
    async def remove_from_queue(self, queue_id: int) -> bool:
        """
        Удаление элемента из очереди.
        
        Args:
            queue_id: ID элемента очереди
            
        Returns:
            bool: True если успешно, False иначе
        """
        queue_item = await self.get_queue_item_by_id(queue_id)
        if not queue_item:
            return False
        
        await self.db.execute(
            delete(NotificationQueue).where(NotificationQueue.id == queue_id)
        )
        await self.db.commit()
        
        return True
    
    async def clear_old_queue_items(self, days: int = 7) -> int:
        """
        Очистка старых элементов очереди.
        
        Args:
            days: Количество дней для очистки
            
        Returns:
            int: Количество удаленных элементов
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Получаем элементы для удаления
        old_items_result = await self.db.execute(
            select(NotificationQueue.id)
            .where(
                and_(
                    NotificationQueue.created_at < cutoff_date,
                    or_(
                        NotificationQueue.is_processing == False,
                        NotificationQueue.attempts >= NotificationQueue.max_attempts
                    )
                )
            )
        )
        old_items = old_items_result.scalars().all()
        
        if not old_items:
            return 0
        
        # Удаляем старые элементы
        await self.db.execute(
            delete(NotificationQueue).where(NotificationQueue.id.in_(old_items))
        )
        await self.db.commit()
        
        return len(old_items)
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """
        Получение статистики очереди.
        
        Returns:
            Dict[str, Any]: Статистика очереди
        """
        # Общее количество элементов в очереди
        total_items_result = await self.db.execute(
            select(func.count(NotificationQueue.id))
        )
        total_items = total_items_result.scalar() or 0
        
        # Элементы по приоритетам
        items_by_priority_result = await self.db.execute(
            select(
                NotificationQueue.priority,
                func.count(NotificationQueue.id).label('count')
            )
            .group_by(NotificationQueue.priority)
        )
        items_by_priority = {row.priority.value: row.count for row in items_by_priority_result}
        
        # Обрабатываемые элементы
        processing_items_result = await self.db.execute(
            select(func.count(NotificationQueue.id))
            .where(NotificationQueue.is_processing == True)
        )
        processing_items = processing_items_result.scalar() or 0
        
        # Элементы, готовые к обработке
        ready_items_result = await self.db.execute(
            select(func.count(NotificationQueue.id))
            .where(
                and_(
                    NotificationQueue.scheduled_at <= datetime.utcnow(),
                    NotificationQueue.is_processing == False,
                    NotificationQueue.attempts < NotificationQueue.max_attempts
                )
            )
        )
        ready_items = ready_items_result.scalar() or 0
        
        # Элементы с ошибками
        failed_items_result = await self.db.execute(
            select(func.count(NotificationQueue.id))
            .where(NotificationQueue.attempts >= NotificationQueue.max_attempts)
        )
        failed_items = failed_items_result.scalar() or 0
        
        return {
            "total_items": total_items,
            "processing_items": processing_items,
            "ready_items": ready_items,
            "failed_items": failed_items,
            "items_by_priority": items_by_priority
        }
    
    async def process_queue_batch(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        Обработка пакета элементов очереди.
        
        Args:
            batch_size: Размер пакета
            
        Returns:
            Dict[str, Any]: Результат обработки
        """
        # Получаем элементы для обработки
        queue_items = await self.get_pending_queue_items(limit=batch_size)
        
        if not queue_items:
            return {
                "processed": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }
        
        processed = 0
        successful = 0
        failed = 0
        errors = []
        
        for queue_item in queue_items:
            try:
                # Отмечаем как обрабатываемый
                await self.mark_as_processing(queue_item.id)
                
                # Получаем уведомление
                notification_result = await self.db.execute(
                    select(Notification).where(Notification.id == queue_item.notification_id)
                )
                notification = notification_result.scalar_one_or_none()
                
                if not notification:
                    await self.mark_as_processed(queue_item.id, success=False, error_message="Уведомление не найдено")
                    failed += 1
                    errors.append(f"Уведомление {queue_item.notification_id} не найдено")
                    continue
                
                # В реальном приложении здесь была бы отправка уведомления
                # Для демонстрации просто помечаем как успешное
                success = True  # Заглушка
                
                if success:
                    # Обновляем статус уведомления
                    await self.db.execute(
                        update(Notification)
                        .where(Notification.id == notification.id)
                        .values(
                            status=NotificationStatus.SENT,
                            sent_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                    )
                    
                    await self.mark_as_processed(queue_item.id, success=True)
                    successful += 1
                else:
                    await self.mark_as_processed(queue_item.id, success=False, error_message="Ошибка отправки")
                    failed += 1
                    errors.append(f"Ошибка отправки уведомления {notification.id}")
                
                processed += 1
                
            except Exception as e:
                await self.mark_as_processed(queue_item.id, success=False, error_message=str(e))
                failed += 1
                errors.append(f"Ошибка обработки элемента очереди {queue_item.id}: {str(e)}")
        
        return {
            "processed": processed,
            "successful": successful,
            "failed": failed,
            "errors": errors
        }
