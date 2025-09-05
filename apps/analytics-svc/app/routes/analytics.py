"""
Роуты для работы с аналитикой.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.stats_service import StatsService
from app.models.analytics import EventType, DeviceType

router = APIRouter()


class ScanEventRequest(BaseModel):
    """Запрос на запись события сканирования."""
    qr_code_id: int = Field(..., description="ID QR кода")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent браузера")
    referer: Optional[str] = Field(None, description="Referer")
    country: Optional[str] = Field(None, description="Страна")
    region: Optional[str] = Field(None, description="Регион")
    city: Optional[str] = Field(None, description="Город")
    latitude: Optional[float] = Field(None, description="Широта")
    longitude: Optional[float] = Field(None, description="Долгота")
    device_type: DeviceType = Field(default=DeviceType.UNKNOWN, description="Тип устройства")
    browser: Optional[str] = Field(None, description="Браузер")
    os: Optional[str] = Field(None, description="Операционная система")
    session_id: Optional[str] = Field(None, description="ID сессии")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class UserActivityRequest(BaseModel):
    """Запрос на запись активности пользователя."""
    user_id: int = Field(..., description="ID пользователя")
    event_type: EventType = Field(..., description="Тип события")
    entity_id: Optional[int] = Field(None, description="ID связанной сущности")
    entity_type: Optional[str] = Field(None, description="Тип сущности")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent браузера")
    session_id: Optional[str] = Field(None, description="ID сессии")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")


class PageViewRequest(BaseModel):
    """Запрос на запись просмотра страницы."""
    page_id: int = Field(..., description="ID страницы")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    duration_seconds: Optional[int] = Field(None, description="Время на странице в секундах")
    is_unique: bool = Field(default=True, description="Уникальный просмотр")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent браузера")
    referer: Optional[str] = Field(None, description="Referer")
    session_id: Optional[str] = Field(None, description="ID сессии")
    country: Optional[str] = Field(None, description="Страна")
    region: Optional[str] = Field(None, description="Регион")
    city: Optional[str] = Field(None, description="Город")
    device_type: DeviceType = Field(default=DeviceType.UNKNOWN, description="Тип устройства")
    browser: Optional[str] = Field(None, description="Браузер")
    os: Optional[str] = Field(None, description="Операционная система")


class AlbumViewRequest(BaseModel):
    """Запрос на запись просмотра альбома."""
    album_id: int = Field(..., description="ID альбома")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    duration_seconds: Optional[int] = Field(None, description="Время в альбоме в секундах")
    pages_viewed: Optional[int] = Field(None, description="Количество просмотренных страниц")
    is_unique: bool = Field(default=True, description="Уникальный просмотр")
    ip_address: Optional[str] = Field(None, description="IP адрес")
    user_agent: Optional[str] = Field(None, description="User Agent браузера")
    referer: Optional[str] = Field(None, description="Referer")
    session_id: Optional[str] = Field(None, description="ID сессии")
    country: Optional[str] = Field(None, description="Страна")
    region: Optional[str] = Field(None, description="Регион")
    city: Optional[str] = Field(None, description="Город")
    device_type: DeviceType = Field(default=DeviceType.UNKNOWN, description="Тип устройства")
    browser: Optional[str] = Field(None, description="Браузер")
    os: Optional[str] = Field(None, description="Операционная система")


@router.post("/analytics/scan", status_code=status.HTTP_201_CREATED)
async def record_scan_event(
    request: ScanEventRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Запись события сканирования QR кода."""
    analytics_service = AnalyticsService(db)
    
    # Получаем IP адрес из запроса, если не указан
    ip_address = request.ip_address
    if not ip_address:
        ip_address = http_request.client.host if http_request.client else None
    
    # Получаем User Agent из запроса, если не указан
    user_agent = request.user_agent
    if not user_agent:
        user_agent = http_request.headers.get("user-agent")
    
    try:
        scan_event = await analytics_service.record_scan_event(
            qr_code_id=request.qr_code_id,
            user_id=request.user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=request.referer,
            country=request.country,
            region=request.region,
            city=request.city,
            latitude=request.latitude,
            longitude=request.longitude,
            device_type=request.device_type,
            browser=request.browser,
            os=request.os,
            session_id=request.session_id,
            extra_data=request.extra_data
        )
        
        return {"message": "Событие сканирования записано", "scan_event_id": scan_event.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при записи события сканирования: {str(e)}"
        )


@router.post("/analytics/activity", status_code=status.HTTP_201_CREATED)
async def record_user_activity(
    request: UserActivityRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Запись активности пользователя."""
    analytics_service = AnalyticsService(db)
    
    # Получаем IP адрес из запроса, если не указан
    ip_address = request.ip_address
    if not ip_address:
        ip_address = http_request.client.host if http_request.client else None
    
    # Получаем User Agent из запроса, если не указан
    user_agent = request.user_agent
    if not user_agent:
        user_agent = http_request.headers.get("user-agent")
    
    try:
        activity = await analytics_service.record_user_activity(
            user_id=request.user_id,
            event_type=request.event_type,
            entity_id=request.entity_id,
            entity_type=request.entity_type,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=request.session_id,
            extra_data=request.extra_data
        )
        
        return {"message": "Активность пользователя записана", "activity_id": activity.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при записи активности пользователя: {str(e)}"
        )


@router.post("/analytics/page-view", status_code=status.HTTP_201_CREATED)
async def record_page_view(
    request: PageViewRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Запись просмотра страницы."""
    analytics_service = AnalyticsService(db)
    
    # Получаем IP адрес из запроса, если не указан
    ip_address = request.ip_address
    if not ip_address:
        ip_address = http_request.client.host if http_request.client else None
    
    # Получаем User Agent из запроса, если не указан
    user_agent = request.user_agent
    if not user_agent:
        user_agent = http_request.headers.get("user-agent")
    
    try:
        page_view = await analytics_service.record_page_view(
            page_id=request.page_id,
            user_id=request.user_id,
            duration_seconds=request.duration_seconds,
            is_unique=request.is_unique,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=request.referer,
            session_id=request.session_id,
            country=request.country,
            region=request.region,
            city=request.city,
            device_type=request.device_type,
            browser=request.browser,
            os=request.os
        )
        
        return {"message": "Просмотр страницы записан", "page_view_id": page_view.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при записи просмотра страницы: {str(e)}"
        )


@router.post("/analytics/album-view", status_code=status.HTTP_201_CREATED)
async def record_album_view(
    request: AlbumViewRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Запись просмотра альбома."""
    analytics_service = AnalyticsService(db)
    
    # Получаем IP адрес из запроса, если не указан
    ip_address = request.ip_address
    if not ip_address:
        ip_address = http_request.client.host if http_request.client else None
    
    # Получаем User Agent из запроса, если не указан
    user_agent = request.user_agent
    if not user_agent:
        user_agent = http_request.headers.get("user-agent")
    
    try:
        album_view = await analytics_service.record_album_view(
            album_id=request.album_id,
            user_id=request.user_id,
            duration_seconds=request.duration_seconds,
            pages_viewed=request.pages_viewed,
            is_unique=request.is_unique,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=request.referer,
            session_id=request.session_id,
            country=request.country,
            region=request.region,
            city=request.city,
            device_type=request.device_type,
            browser=request.browser,
            os=request.os
        )
        
        return {"message": "Просмотр альбома записан", "album_view_id": album_view.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при записи просмотра альбома: {str(e)}"
        )


@router.get("/analytics/scan-events")
async def get_scan_events(
    qr_code_id: Optional[int] = Query(None, description="ID QR кода для фильтрации"),
    user_id: Optional[int] = Query(None, description="ID пользователя для фильтрации"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение событий сканирования."""
    analytics_service = AnalyticsService(db)
    
    try:
        scan_events = await analytics_service.get_scan_events(
            qr_code_id=qr_code_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return [event.to_dict() for event in scan_events]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении событий сканирования: {str(e)}"
        )


@router.get("/analytics/user-activities")
async def get_user_activities(
    user_id: int = Query(..., description="ID пользователя"),
    event_type: Optional[EventType] = Query(None, description="Тип события для фильтрации"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение активности пользователя."""
    analytics_service = AnalyticsService(db)
    
    try:
        activities = await analytics_service.get_user_activities(
            user_id=user_id,
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return [activity.to_dict() for activity in activities]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении активности пользователя: {str(e)}"
        )


@router.get("/analytics/page-views")
async def get_page_views(
    page_id: Optional[int] = Query(None, description="ID страницы для фильтрации"),
    user_id: Optional[int] = Query(None, description="ID пользователя для фильтрации"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение просмотров страниц."""
    analytics_service = AnalyticsService(db)
    
    try:
        page_views = await analytics_service.get_page_views(
            page_id=page_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return [view.to_dict() for view in page_views]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении просмотров страниц: {str(e)}"
        )


@router.get("/analytics/album-views")
async def get_album_views(
    album_id: Optional[int] = Query(None, description="ID альбома для фильтрации"),
    user_id: Optional[int] = Query(None, description="ID пользователя для фильтрации"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение просмотров альбомов."""
    analytics_service = AnalyticsService(db)
    
    try:
        album_views = await analytics_service.get_album_views(
            album_id=album_id,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return [view.to_dict() for view in album_views]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении просмотров альбомов: {str(e)}"
        )
