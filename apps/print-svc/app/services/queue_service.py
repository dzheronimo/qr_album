"""
Сервис для работы с очередью печати.

Содержит бизнес-логику для управления очередью заданий печати.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.print_models import PrintQueue, PrintJob, PrintJobStatus


class QueueService:
    """Сервис для работы с очередью печати."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def add_to_queue(
        self,
        job_id: int,
        priority: int = 1,
        scheduled_at: Optional[datetime] = None
    ) -> PrintQueue:
        """
        Добавление задания в очередь.
        
        Args:
            job_id: ID задания печати
            priority: Приоритет (1-5)
            scheduled_at: Время планируемого выполнения
            
        Returns:
            PrintQueue: Элемент очереди
        """
        queue_item = PrintQueue(
            job_id=job_id,
            priority=priority,
            scheduled_at=scheduled_at
        )
        
        try:
            self.db.add(queue_item)
            await self.db.commit()
            await self.db.refresh(queue_item)
            return queue_item
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Задание уже находится в очереди")
    
    async def get_next_job(
        self,
        worker_id: str,
        max_attempts: int = 3
    ) -> Optional[PrintQueue]:
        """
        Получение следующего задания из очереди.
        
        Args:
            worker_id: ID воркера
            max_attempts: Максимальное количество попыток
            
        Returns:
            Optional[PrintQueue]: Элемент очереди или None
        """
        # Ищем задание с наивысшим приоритетом
        result = await self.db.execute(
            select(PrintQueue)
            .join(PrintJob, PrintQueue.job_id == PrintJob.id)
            .where(
                and_(
                    PrintQueue.is_processing == False,
                    PrintQueue.attempts < max_attempts,
                    or_(
                        PrintQueue.scheduled_at.is_(None),
                        PrintQueue.scheduled_at <= datetime.utcnow()
                    ),
                    PrintJob.status == PrintJobStatus.PENDING
                )
            )
            .order_by(PrintQueue.priority.desc(), PrintQueue.created_at.asc())
            .limit(1)
        )
        
        queue_item = result.scalar_one_or_none()
        if not queue_item:
            return None
        
        # Помечаем как обрабатываемое
        await self.db.execute(
            update(PrintQueue)
            .where(PrintQueue.id == queue_item.id)
            .values(
                is_processing=True,
                worker_id=worker_id,
                attempts=PrintQueue.attempts + 1,
                last_attempt_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        # Обновляем объект
        await self.db.refresh(queue_item)
        return queue_item
    
    async def mark_job_completed(
        self,
        job_id: int,
        success: bool = True
    ) -> bool:
        """
        Отметка задания как завершенного.
        
        Args:
            job_id: ID задания
            success: Успешность выполнения
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            # Удаляем из очереди
            await self.db.execute(
                delete(PrintQueue).where(PrintQueue.job_id == job_id)
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def mark_job_failed(
        self,
        job_id: int,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Отметка задания как неудачного.
        
        Args:
            job_id: ID задания
            error_message: Сообщение об ошибке
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            # Сбрасываем флаг обработки
            await self.db.execute(
                update(PrintQueue)
                .where(PrintQueue.job_id == job_id)
                .values(
                    is_processing=False,
                    worker_id=None,
                    updated_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """
        Получение статуса очереди.
        
        Returns:
            Dict[str, Any]: Статус очереди
        """
        # Общее количество заданий в очереди
        total_in_queue_result = await self.db.execute(
            select(func.count(PrintQueue.id))
        )
        total_in_queue = total_in_queue_result.scalar() or 0
        
        # Задания в обработке
        processing_result = await self.db.execute(
            select(func.count(PrintQueue.id))
            .where(PrintQueue.is_processing == True)
        )
        processing = processing_result.scalar() or 0
        
        # Задания по приоритетам
        by_priority_result = await self.db.execute(
            select(
                PrintQueue.priority,
                func.count(PrintQueue.id).label('count')
            )
            .where(PrintQueue.is_processing == False)
            .group_by(PrintQueue.priority)
        )
        by_priority = {row.priority: row.count for row in by_priority_result}
        
        # Задания с ошибками
        failed_result = await self.db.execute(
            select(func.count(PrintQueue.id))
            .where(PrintQueue.attempts >= PrintQueue.max_attempts)
        )
        failed = failed_result.scalar() or 0
        
        return {
            "total_in_queue": total_in_queue,
            "processing": processing,
            "waiting": total_in_queue - processing,
            "by_priority": by_priority,
            "failed": failed
        }
    
    async def get_queue_items(
        self,
        is_processing: Optional[bool] = None,
        priority: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[PrintQueue]:
        """
        Получение элементов очереди.
        
        Args:
            is_processing: Фильтр по статусу обработки
            priority: Фильтр по приоритету
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[PrintQueue]: Список элементов очереди
        """
        query = select(PrintQueue)
        conditions = []
        
        if is_processing is not None:
            conditions.append(PrintQueue.is_processing == is_processing)
        if priority is not None:
            conditions.append(PrintQueue.priority == priority)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PrintQueue.priority.desc(), PrintQueue.created_at.asc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def cleanup_old_queue_items(self, hours: int = 24) -> int:
        """
        Очистка старых элементов очереди.
        
        Args:
            hours: Количество часов для хранения
            
        Returns:
            int: Количество удаленных элементов
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Получаем старые элементы
        old_items_result = await self.db.execute(
            select(PrintQueue.id)
            .where(
                and_(
                    PrintQueue.created_at < cutoff_time,
                    PrintQueue.is_processing == False
                )
            )
        )
        old_items = old_items_result.scalars().all()
        
        if not old_items:
            return 0
        
        # Удаляем старые элементы
        await self.db.execute(
            delete(PrintQueue).where(PrintQueue.id.in_(old_items))
        )
        await self.db.commit()
        
        return len(old_items)
    
    async def reschedule_job(
        self,
        job_id: int,
        scheduled_at: datetime
    ) -> bool:
        """
        Перенос задания на другое время.
        
        Args:
            job_id: ID задания
            scheduled_at: Новое время выполнения
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            await self.db.execute(
                update(PrintQueue)
                .where(PrintQueue.job_id == job_id)
                .values(
                    scheduled_at=scheduled_at,
                    updated_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def change_job_priority(
        self,
        job_id: int,
        priority: int
    ) -> bool:
        """
        Изменение приоритета задания.
        
        Args:
            job_id: ID задания
            priority: Новый приоритет
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            await self.db.execute(
                update(PrintQueue)
                .where(PrintQueue.job_id == job_id)
                .values(
                    priority=priority,
                    updated_at=datetime.utcnow()
                )
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def remove_from_queue(self, job_id: int) -> bool:
        """
        Удаление задания из очереди.
        
        Args:
            job_id: ID задания
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            await self.db.execute(
                delete(PrintQueue).where(PrintQueue.job_id == job_id)
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """
        Получение статистики очереди.
        
        Returns:
            Dict[str, Any]: Статистика очереди
        """
        # Общее количество заданий в очереди
        total_in_queue_result = await self.db.execute(
            select(func.count(PrintQueue.id))
        )
        total_in_queue = total_in_queue_result.scalar() or 0
        
        # Задания в обработке
        processing_result = await self.db.execute(
            select(func.count(PrintQueue.id))
            .where(PrintQueue.is_processing == True)
        )
        processing = processing_result.scalar() or 0
        
        # Задания по приоритетам
        by_priority_result = await self.db.execute(
            select(
                PrintQueue.priority,
                func.count(PrintQueue.id).label('count')
            )
            .where(PrintQueue.is_processing == False)
            .group_by(PrintQueue.priority)
        )
        by_priority = {row.priority: row.count for row in by_priority_result}
        
        # Задания с ошибками
        failed_result = await self.db.execute(
            select(func.count(PrintQueue.id))
            .where(PrintQueue.attempts >= PrintQueue.max_attempts)
        )
        failed = failed_result.scalar() or 0
        
        # Среднее время ожидания
        avg_wait_time_result = await self.db.execute(
            select(func.avg(
                func.extract('epoch', datetime.utcnow() - PrintQueue.created_at)
            ))
            .where(PrintQueue.is_processing == False)
        )
        avg_wait_time = avg_wait_time_result.scalar() or 0
        
        return {
            "total_in_queue": total_in_queue,
            "processing": processing,
            "waiting": total_in_queue - processing,
            "by_priority": by_priority,
            "failed": failed,
            "average_wait_time_seconds": round(avg_wait_time, 2)
        }
