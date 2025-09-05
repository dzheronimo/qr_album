"""
Сервис для работы со статистикой.

Содержит бизнес-логику для генерации статистики и аналитики.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload

from app.models.analytics import ScanEvent, UserActivity, PageView, AlbumView, EventType, DeviceType


class StatsService:
    """Сервис для работы со статистикой."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def get_qr_code_stats(
        self,
        qr_code_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Получение статистики по QR коду.
        
        Args:
            qr_code_id: ID QR кода
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Dict[str, Any]: Статистика по QR коду
        """
        # Базовый запрос
        query = select(ScanEvent).where(ScanEvent.qr_code_id == qr_code_id)
        
        if start_date:
            query = query.where(ScanEvent.scan_timestamp >= start_date)
        if end_date:
            query = query.where(ScanEvent.scan_timestamp <= end_date)
        
        # Общее количество сканирований
        total_scans_result = await self.db.execute(
            select(func.count(ScanEvent.id)).where(ScanEvent.qr_code_id == qr_code_id)
        )
        total_scans = total_scans_result.scalar() or 0
        
        # Уникальные сканирования (по IP)
        unique_scans_result = await self.db.execute(
            select(func.count(func.distinct(ScanEvent.ip_address)))
            .where(ScanEvent.qr_code_id == qr_code_id)
        )
        unique_scans = unique_scans_result.scalar() or 0
        
        # Статистика по устройствам
        device_stats_result = await self.db.execute(
            select(
                ScanEvent.device_type,
                func.count(ScanEvent.id).label('count')
            )
            .where(ScanEvent.qr_code_id == qr_code_id)
            .group_by(ScanEvent.device_type)
        )
        device_stats = {row.device_type.value: row.count for row in device_stats_result}
        
        # Статистика по странам
        country_stats_result = await self.db.execute(
            select(
                ScanEvent.country,
                func.count(ScanEvent.id).label('count')
            )
            .where(and_(ScanEvent.qr_code_id == qr_code_id, ScanEvent.country.isnot(None)))
            .group_by(ScanEvent.country)
            .order_by(desc('count'))
            .limit(10)
        )
        country_stats = {row.country: row.count for row in country_stats_result}
        
        # Статистика по браузерам
        browser_stats_result = await self.db.execute(
            select(
                ScanEvent.browser,
                func.count(ScanEvent.id).label('count')
            )
            .where(and_(ScanEvent.qr_code_id == qr_code_id, ScanEvent.browser.isnot(None)))
            .group_by(ScanEvent.browser)
            .order_by(desc('count'))
            .limit(10)
        )
        browser_stats = {row.browser: row.count for row in browser_stats_result}
        
        # Последнее сканирование
        last_scan_result = await self.db.execute(
            select(ScanEvent)
            .where(ScanEvent.qr_code_id == qr_code_id)
            .order_by(desc(ScanEvent.scan_timestamp))
            .limit(1)
        )
        last_scan = last_scan_result.scalar_one_or_none()
        
        return {
            "qr_code_id": qr_code_id,
            "total_scans": total_scans,
            "unique_scans": unique_scans,
            "device_stats": device_stats,
            "country_stats": country_stats,
            "browser_stats": browser_stats,
            "last_scan": last_scan.to_dict() if last_scan else None,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_user_stats(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Получение статистики пользователя.
        
        Args:
            user_id: ID пользователя
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Dict[str, Any]: Статистика пользователя
        """
        # Статистика активности
        activity_stats_result = await self.db.execute(
            select(
                UserActivity.event_type,
                func.count(UserActivity.id).label('count')
            )
            .where(UserActivity.user_id == user_id)
            .group_by(UserActivity.event_type)
        )
        activity_stats = {row.event_type.value: row.count for row in activity_stats_result}
        
        # Статистика просмотров страниц
        page_views_result = await self.db.execute(
            select(func.count(PageView.id))
            .where(PageView.user_id == user_id)
        )
        total_page_views = page_views_result.scalar() or 0
        
        # Статистика просмотров альбомов
        album_views_result = await self.db.execute(
            select(func.count(AlbumView.id))
            .where(AlbumView.user_id == user_id)
        )
        total_album_views = album_views_result.scalar() or 0
        
        # Среднее время на странице
        avg_page_duration_result = await self.db.execute(
            select(func.avg(PageView.duration_seconds))
            .where(and_(PageView.user_id == user_id, PageView.duration_seconds.isnot(None)))
        )
        avg_page_duration = avg_page_duration_result.scalar() or 0
        
        # Среднее время в альбоме
        avg_album_duration_result = await self.db.execute(
            select(func.avg(AlbumView.duration_seconds))
            .where(and_(AlbumView.user_id == user_id, AlbumView.duration_seconds.isnot(None)))
        )
        avg_album_duration = avg_album_duration_result.scalar() or 0
        
        return {
            "user_id": user_id,
            "activity_stats": activity_stats,
            "total_page_views": total_page_views,
            "total_album_views": total_album_views,
            "avg_page_duration_seconds": round(avg_page_duration, 2),
            "avg_album_duration_seconds": round(avg_album_duration, 2),
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_album_stats(
        self,
        album_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Получение статистики альбома.
        
        Args:
            album_id: ID альбома
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Dict[str, Any]: Статистика альбома
        """
        # Общее количество просмотров
        total_views_result = await self.db.execute(
            select(func.count(AlbumView.id))
            .where(AlbumView.album_id == album_id)
        )
        total_views = total_views_result.scalar() or 0
        
        # Уникальные просмотры
        unique_views_result = await self.db.execute(
            select(func.count(func.distinct(AlbumView.ip_address)))
            .where(AlbumView.album_id == album_id)
        )
        unique_views = unique_views_result.scalar() or 0
        
        # Среднее время в альбоме
        avg_duration_result = await self.db.execute(
            select(func.avg(AlbumView.duration_seconds))
            .where(and_(AlbumView.album_id == album_id, AlbumView.duration_seconds.isnot(None)))
        )
        avg_duration = avg_duration_result.scalar() or 0
        
        # Среднее количество просмотренных страниц
        avg_pages_viewed_result = await self.db.execute(
            select(func.avg(AlbumView.pages_viewed))
            .where(and_(AlbumView.album_id == album_id, AlbumView.pages_viewed.isnot(None)))
        )
        avg_pages_viewed = avg_pages_viewed_result.scalar() or 0
        
        # Статистика по устройствам
        device_stats_result = await self.db.execute(
            select(
                AlbumView.device_type,
                func.count(AlbumView.id).label('count')
            )
            .where(AlbumView.album_id == album_id)
            .group_by(AlbumView.device_type)
        )
        device_stats = {row.device_type.value: row.count for row in device_stats_result}
        
        # Статистика по странам
        country_stats_result = await self.db.execute(
            select(
                AlbumView.country,
                func.count(AlbumView.id).label('count')
            )
            .where(and_(AlbumView.album_id == album_id, AlbumView.country.isnot(None)))
            .group_by(AlbumView.country)
            .order_by(desc('count'))
            .limit(10)
        )
        country_stats = {row.country: row.count for row in country_stats_result}
        
        return {
            "album_id": album_id,
            "total_views": total_views,
            "unique_views": unique_views,
            "avg_duration_seconds": round(avg_duration, 2),
            "avg_pages_viewed": round(avg_pages_viewed, 2),
            "device_stats": device_stats,
            "country_stats": country_stats,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_page_stats(
        self,
        page_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Получение статистики страницы.
        
        Args:
            page_id: ID страницы
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Dict[str, Any]: Статистика страницы
        """
        # Общее количество просмотров
        total_views_result = await self.db.execute(
            select(func.count(PageView.id))
            .where(PageView.page_id == page_id)
        )
        total_views = total_views_result.scalar() or 0
        
        # Уникальные просмотры
        unique_views_result = await self.db.execute(
            select(func.count(func.distinct(PageView.ip_address)))
            .where(PageView.page_id == page_id)
        )
        unique_views = unique_views_result.scalar() or 0
        
        # Среднее время на странице
        avg_duration_result = await self.db.execute(
            select(func.avg(PageView.duration_seconds))
            .where(and_(PageView.page_id == page_id, PageView.duration_seconds.isnot(None)))
        )
        avg_duration = avg_duration_result.scalar() or 0
        
        # Статистика по устройствам
        device_stats_result = await self.db.execute(
            select(
                PageView.device_type,
                func.count(PageView.id).label('count')
            )
            .where(PageView.page_id == page_id)
            .group_by(PageView.device_type)
        )
        device_stats = {row.device_type.value: row.count for row in device_stats_result}
        
        # Статистика по странам
        country_stats_result = await self.db.execute(
            select(
                PageView.country,
                func.count(PageView.id).label('count')
            )
            .where(and_(PageView.page_id == page_id, PageView.country.isnot(None)))
            .group_by(PageView.country)
            .order_by(desc('count'))
            .limit(10)
        )
        country_stats = {row.country: row.count for row in country_stats_result}
        
        return {
            "page_id": page_id,
            "total_views": total_views,
            "unique_views": unique_views,
            "avg_duration_seconds": round(avg_duration, 2),
            "device_stats": device_stats,
            "country_stats": country_stats,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    async def get_daily_stats(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Получение ежедневной статистики.
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата (по умолчанию - сегодня)
            
        Returns:
            Dict[str, Any]: Ежедневная статистика
        """
        if end_date is None:
            end_date = datetime.utcnow()
        
        # Статистика сканирований по дням
        daily_scans_result = await self.db.execute(
            select(
                func.date(ScanEvent.scan_timestamp).label('date'),
                func.count(ScanEvent.id).label('scans')
            )
            .where(and_(
                ScanEvent.scan_timestamp >= start_date,
                ScanEvent.scan_timestamp <= end_date
            ))
            .group_by(func.date(ScanEvent.scan_timestamp))
            .order_by('date')
        )
        daily_scans = {row.date.isoformat(): row.scans for row in daily_scans_result}
        
        # Статистика просмотров страниц по дням
        daily_page_views_result = await self.db.execute(
            select(
                func.date(PageView.view_timestamp).label('date'),
                func.count(PageView.id).label('views')
            )
            .where(and_(
                PageView.view_timestamp >= start_date,
                PageView.view_timestamp <= end_date
            ))
            .group_by(func.date(PageView.view_timestamp))
            .order_by('date')
        )
        daily_page_views = {row.date.isoformat(): row.views for row in daily_page_views_result}
        
        # Статистика просмотров альбомов по дням
        daily_album_views_result = await self.db.execute(
            select(
                func.date(AlbumView.view_timestamp).label('date'),
                func.count(AlbumView.id).label('views')
            )
            .where(and_(
                AlbumView.view_timestamp >= start_date,
                AlbumView.view_timestamp <= end_date
            ))
            .group_by(func.date(AlbumView.view_timestamp))
            .order_by('date')
        )
        daily_album_views = {row.date.isoformat(): row.views for row in daily_album_views_result}
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "daily_scans": daily_scans,
            "daily_page_views": daily_page_views,
            "daily_album_views": daily_album_views
        }
    
    async def get_top_content(
        self,
        content_type: str = "albums",
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Получение топ контента.
        
        Args:
            content_type: Тип контента ("albums" или "pages")
            limit: Количество записей
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            List[Dict[str, Any]]: Топ контента
        """
        if content_type == "albums":
            query = select(
                AlbumView.album_id,
                func.count(AlbumView.id).label('views'),
                func.count(func.distinct(AlbumView.ip_address)).label('unique_views'),
                func.avg(AlbumView.duration_seconds).label('avg_duration')
            ).group_by(AlbumView.album_id)
            
            if start_date:
                query = query.where(AlbumView.view_timestamp >= start_date)
            if end_date:
                query = query.where(AlbumView.view_timestamp <= end_date)
            
            query = query.order_by(desc('views')).limit(limit)
            
            result = await self.db.execute(query)
            return [
                {
                    "album_id": row.album_id,
                    "views": row.views,
                    "unique_views": row.unique_views,
                    "avg_duration_seconds": round(row.avg_duration or 0, 2)
                }
                for row in result
            ]
        
        elif content_type == "pages":
            query = select(
                PageView.page_id,
                func.count(PageView.id).label('views'),
                func.count(func.distinct(PageView.ip_address)).label('unique_views'),
                func.avg(PageView.duration_seconds).label('avg_duration')
            ).group_by(PageView.page_id)
            
            if start_date:
                query = query.where(PageView.view_timestamp >= start_date)
            if end_date:
                query = query.where(PageView.view_timestamp <= end_date)
            
            query = query.order_by(desc('views')).limit(limit)
            
            result = await self.db.execute(query)
            return [
                {
                    "page_id": row.page_id,
                    "views": row.views,
                    "unique_views": row.unique_views,
                    "avg_duration_seconds": round(row.avg_duration or 0, 2)
                }
                for row in result
            ]
        
        return []
