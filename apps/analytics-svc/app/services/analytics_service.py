"""
Сервис для работы с аналитикой.

Содержит бизнес-логику для отслеживания событий и активности.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.exc import IntegrityError

from app.models.analytics import ScanEvent, UserActivity, PageView, AlbumView, EventType, DeviceType


class AnalyticsService:
    """Сервис для работы с аналитикой."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def record_scan_event(
        self,
        qr_code_id: int,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        device_type: DeviceType = DeviceType.UNKNOWN,
        browser: Optional[str] = None,
        os: Optional[str] = None,
        session_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> ScanEvent:
        """
        Запись события сканирования QR кода.
        
        Args:
            qr_code_id: ID QR кода
            user_id: ID пользователя (если авторизован)
            ip_address: IP адрес
            user_agent: User Agent браузера
            referer: Referer
            country: Страна
            region: Регион
            city: Город
            latitude: Широта
            longitude: Долгота
            device_type: Тип устройства
            browser: Браузер
            os: Операционная система
            session_id: ID сессии
            extra_data: Дополнительные данные
            
        Returns:
            ScanEvent: Созданное событие сканирования
        """
        scan_event = ScanEvent(
            qr_code_id=qr_code_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            country=country,
            region=region,
            city=city,
            latitude=latitude,
            longitude=longitude,
            device_type=device_type,
            browser=browser,
            os=os,
            session_id=session_id,
            extra_data=extra_data
        )
        
        self.db.add(scan_event)
        await self.db.commit()
        await self.db.refresh(scan_event)
        
        return scan_event
    
    async def record_user_activity(
        self,
        user_id: int,
        event_type: EventType,
        entity_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> UserActivity:
        """
        Запись активности пользователя.
        
        Args:
            user_id: ID пользователя
            event_type: Тип события
            entity_id: ID связанной сущности
            entity_type: Тип сущности
            ip_address: IP адрес
            user_agent: User Agent браузера
            session_id: ID сессии
            extra_data: Дополнительные метаданные
            
        Returns:
            UserActivity: Созданная активность
        """
        activity = UserActivity(
            user_id=user_id,
            event_type=event_type,
            entity_id=entity_id,
            entity_type=entity_type,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            extra_data=extra_data
        )
        
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        
        return activity
    
    async def record_page_view(
        self,
        page_id: int,
        user_id: Optional[int] = None,
        duration_seconds: Optional[int] = None,
        is_unique: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        session_id: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        city: Optional[str] = None,
        device_type: DeviceType = DeviceType.UNKNOWN,
        browser: Optional[str] = None,
        os: Optional[str] = None
    ) -> PageView:
        """
        Запись просмотра страницы.
        
        Args:
            page_id: ID страницы
            user_id: ID пользователя
            duration_seconds: Время на странице в секундах
            is_unique: Уникальный просмотр
            ip_address: IP адрес
            user_agent: User Agent браузера
            referer: Referer
            session_id: ID сессии
            country: Страна
            region: Регион
            city: Город
            device_type: Тип устройства
            browser: Браузер
            os: Операционная система
            
        Returns:
            PageView: Созданный просмотр страницы
        """
        page_view = PageView(
            page_id=page_id,
            user_id=user_id,
            duration_seconds=duration_seconds,
            is_unique=is_unique,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            session_id=session_id,
            country=country,
            region=region,
            city=city,
            device_type=device_type,
            browser=browser,
            os=os
        )
        
        self.db.add(page_view)
        await self.db.commit()
        await self.db.refresh(page_view)
        
        return page_view
    
    async def record_album_view(
        self,
        album_id: int,
        user_id: Optional[int] = None,
        duration_seconds: Optional[int] = None,
        pages_viewed: Optional[int] = None,
        is_unique: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        session_id: Optional[str] = None,
        country: Optional[str] = None,
        region: Optional[str] = None,
        city: Optional[str] = None,
        device_type: DeviceType = DeviceType.UNKNOWN,
        browser: Optional[str] = None,
        os: Optional[str] = None
    ) -> AlbumView:
        """
        Запись просмотра альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            duration_seconds: Время в альбоме в секундах
            pages_viewed: Количество просмотренных страниц
            is_unique: Уникальный просмотр
            ip_address: IP адрес
            user_agent: User Agent браузера
            referer: Referer
            session_id: ID сессии
            country: Страна
            region: Регион
            city: Город
            device_type: Тип устройства
            browser: Браузер
            os: Операционная система
            
        Returns:
            AlbumView: Созданный просмотр альбома
        """
        album_view = AlbumView(
            album_id=album_id,
            user_id=user_id,
            duration_seconds=duration_seconds,
            pages_viewed=pages_viewed,
            is_unique=is_unique,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            session_id=session_id,
            country=country,
            region=region,
            city=city,
            device_type=device_type,
            browser=browser,
            os=os
        )
        
        self.db.add(album_view)
        await self.db.commit()
        await self.db.refresh(album_view)
        
        return album_view
    
    async def get_scan_events(
        self,
        qr_code_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ScanEvent]:
        """
        Получение событий сканирования.
        
        Args:
            qr_code_id: ID QR кода для фильтрации
            user_id: ID пользователя для фильтрации
            start_date: Начальная дата
            end_date: Конечная дата
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ScanEvent]: Список событий сканирования
        """
        query = select(ScanEvent)
        
        conditions = []
        if qr_code_id is not None:
            conditions.append(ScanEvent.qr_code_id == qr_code_id)
        if user_id is not None:
            conditions.append(ScanEvent.user_id == user_id)
        if start_date is not None:
            conditions.append(ScanEvent.scan_timestamp >= start_date)
        if end_date is not None:
            conditions.append(ScanEvent.scan_timestamp <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ScanEvent.scan_timestamp.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_activities(
        self,
        user_id: int,
        event_type: Optional[EventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserActivity]:
        """
        Получение активности пользователя.
        
        Args:
            user_id: ID пользователя
            event_type: Тип события для фильтрации
            start_date: Начальная дата
            end_date: Конечная дата
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[UserActivity]: Список активности пользователя
        """
        query = select(UserActivity).where(UserActivity.user_id == user_id)
        
        conditions = []
        if event_type is not None:
            conditions.append(UserActivity.event_type == event_type)
        if start_date is not None:
            conditions.append(UserActivity.event_timestamp >= start_date)
        if end_date is not None:
            conditions.append(UserActivity.event_timestamp <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(UserActivity.event_timestamp.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_page_views(
        self,
        page_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PageView]:
        """
        Получение просмотров страниц.
        
        Args:
            page_id: ID страницы для фильтрации
            user_id: ID пользователя для фильтрации
            start_date: Начальная дата
            end_date: Конечная дата
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[PageView]: Список просмотров страниц
        """
        query = select(PageView)
        
        conditions = []
        if page_id is not None:
            conditions.append(PageView.page_id == page_id)
        if user_id is not None:
            conditions.append(PageView.user_id == user_id)
        if start_date is not None:
            conditions.append(PageView.view_timestamp >= start_date)
        if end_date is not None:
            conditions.append(PageView.view_timestamp <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PageView.view_timestamp.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_album_views(
        self,
        album_id: Optional[int] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AlbumView]:
        """
        Получение просмотров альбомов.
        
        Args:
            album_id: ID альбома для фильтрации
            user_id: ID пользователя для фильтрации
            start_date: Начальная дата
            end_date: Конечная дата
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[AlbumView]: Список просмотров альбомов
        """
        query = select(AlbumView)
        
        conditions = []
        if album_id is not None:
            conditions.append(AlbumView.album_id == album_id)
        if user_id is not None:
            conditions.append(AlbumView.user_id == user_id)
        if start_date is not None:
            conditions.append(AlbumView.view_timestamp >= start_date)
        if end_date is not None:
            conditions.append(AlbumView.view_timestamp <= end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(AlbumView.view_timestamp.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
