"""
Сервис для работы с журналом модерации.

Содержит бизнес-логику для логирования действий модерации.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.moderation import ModerationLog, ModerationRequest


class LogService:
    """Сервис для работы с журналом модерации."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def log_action(
        self,
        request_id: int,
        action: str,
        actor_type: str,
        actor_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> ModerationLog:
        """
        Логирование действия модерации.
        
        Args:
            request_id: ID запроса на модерацию
            action: Действие
            actor_type: Тип исполнителя (user, ai, system, moderator)
            actor_id: ID исполнителя
            details: Детали действия
            message: Сообщение
            ip_address: IP адрес
            user_agent: User Agent
            
        Returns:
            ModerationLog: Запись в журнале
        """
        log_entry = ModerationLog(
            request_id=request_id,
            action=action,
            actor_type=actor_type,
            actor_id=actor_id,
            details=details,
            message=message,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        try:
            self.db.add(log_entry)
            await self.db.commit()
            await self.db.refresh(log_entry)
            return log_entry
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании записи в журнале")
    
    async def get_logs_by_request(
        self,
        request_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[ModerationLog]:
        """
        Получение записей журнала для запроса.
        
        Args:
            request_id: ID запроса
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationLog]: Список записей журнала
        """
        result = await self.db.execute(
            select(ModerationLog)
            .where(ModerationLog.request_id == request_id)
            .order_by(ModerationLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_logs_by_actor(
        self,
        actor_type: str,
        actor_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ModerationLog]:
        """
        Получение записей журнала по исполнителю.
        
        Args:
            actor_type: Тип исполнителя
            actor_id: ID исполнителя
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationLog]: Список записей журнала
        """
        query = select(ModerationLog).where(ModerationLog.actor_type == actor_type)
        
        if actor_id is not None:
            query = query.where(ModerationLog.actor_id == actor_id)
        
        query = query.order_by(ModerationLog.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_logs_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[ModerationLog]:
        """
        Получение записей журнала по действию.
        
        Args:
            action: Действие
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationLog]: Список записей журнала
        """
        result = await self.db.execute(
            select(ModerationLog)
            .where(ModerationLog.action == action)
            .order_by(ModerationLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent_logs(
        self,
        hours: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModerationLog]:
        """
        Получение недавних записей журнала.
        
        Args:
            hours: Количество часов назад
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationLog]: Список записей журнала
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.db.execute(
            select(ModerationLog)
            .where(ModerationLog.created_at >= since)
            .order_by(ModerationLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_logs(
        self,
        query_text: Optional[str] = None,
        actor_type: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ModerationLog]:
        """
        Поиск записей журнала.
        
        Args:
            query_text: Текст для поиска в сообщениях
            actor_type: Тип исполнителя
            action: Действие
            start_date: Начальная дата
            end_date: Конечная дата
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationLog]: Список записей журнала
        """
        query = select(ModerationLog)
        conditions = []
        
        if query_text:
            conditions.append(
                or_(
                    ModerationLog.message.ilike(f"%{query_text}%"),
                    ModerationLog.details.cast(String).ilike(f"%{query_text}%")
                )
            )
        
        if actor_type:
            conditions.append(ModerationLog.actor_type == actor_type)
        
        if action:
            conditions.append(ModerationLog.action == action)
        
        if start_date:
            conditions.append(ModerationLog.created_at >= start_date)
        
        if end_date:
            conditions.append(ModerationLog.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ModerationLog.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_log_stats(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Получение статистики журнала.
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Dict[str, Any]: Статистика журнала
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Общее количество записей
        total_logs_result = await self.db.execute(
            select(func.count(ModerationLog.id))
            .where(ModerationLog.created_at >= since)
        )
        total_logs = total_logs_result.scalar() or 0
        
        # Записи по типам исполнителей
        logs_by_actor_type_result = await self.db.execute(
            select(
                ModerationLog.actor_type,
                func.count(ModerationLog.id).label('count')
            )
            .where(ModerationLog.created_at >= since)
            .group_by(ModerationLog.actor_type)
        )
        logs_by_actor_type = {row.actor_type: row.count for row in logs_by_actor_type_result}
        
        # Записи по действиям
        logs_by_action_result = await self.db.execute(
            select(
                ModerationLog.action,
                func.count(ModerationLog.id).label('count')
            )
            .where(ModerationLog.created_at >= since)
            .group_by(ModerationLog.action)
        )
        logs_by_action = {row.action: row.count for row in logs_by_action_result}
        
        # Активность по дням
        daily_activity_result = await self.db.execute(
            select(
                func.date(ModerationLog.created_at).label('date'),
                func.count(ModerationLog.id).label('count')
            )
            .where(ModerationLog.created_at >= since)
            .group_by(func.date(ModerationLog.created_at))
            .order_by(func.date(ModerationLog.created_at))
        )
        daily_activity = [
            {
                "date": row.date.isoformat(),
                "count": row.count
            }
            for row in daily_activity_result
        ]
        
        return {
            "total_logs": total_logs,
            "logs_by_actor_type": logs_by_actor_type,
            "logs_by_action": logs_by_action,
            "daily_activity": daily_activity,
            "period_days": days
        }
    
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """
        Очистка старых записей журнала.
        
        Args:
            days: Количество дней для хранения
            
        Returns:
            int: Количество удаленных записей
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Получаем записи для удаления
        old_logs_result = await self.db.execute(
            select(ModerationLog.id)
            .where(ModerationLog.created_at < cutoff_date)
        )
        old_logs = old_logs_result.scalars().all()
        
        if not old_logs:
            return 0
        
        # Удаляем старые записи
        from sqlalchemy import delete
        await self.db.execute(
            delete(ModerationLog).where(ModerationLog.id.in_(old_logs))
        )
        await self.db.commit()
        
        return len(old_logs)
    
    async def export_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> List[Dict[str, Any]]:
        """
        Экспорт записей журнала.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            format: Формат экспорта (json, csv)
            
        Returns:
            List[Dict[str, Any]]: Экспортированные данные
        """
        query = select(ModerationLog)
        conditions = []
        
        if start_date:
            conditions.append(ModerationLog.created_at >= start_date)
        
        if end_date:
            conditions.append(ModerationLog.created_at <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ModerationLog.created_at.desc())
        
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        if format == "json":
            return [log.to_dict() for log in logs]
        else:
            # Для CSV можно добавить специальную обработку
            return [log.to_dict() for log in logs]
