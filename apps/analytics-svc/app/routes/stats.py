"""
Роуты для работы со статистикой.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.stats_service import StatsService
from app.dependencies import get_current_user_id

router = APIRouter()


class QRCodeStatsResponse(BaseModel):
    """Ответ со статистикой QR кода."""
    qr_code_id: int
    total_scans: int
    unique_scans: int
    device_stats: Dict[str, int]
    country_stats: Dict[str, int]
    browser_stats: Dict[str, int]
    last_scan: Optional[Dict[str, Any]]
    period: Dict[str, Optional[str]]


class UserStatsResponse(BaseModel):
    """Ответ со статистикой пользователя."""
    user_id: int
    activity_stats: Dict[str, int]
    total_page_views: int
    total_album_views: int
    avg_page_duration_seconds: float
    avg_album_duration_seconds: float
    period: Dict[str, Optional[str]]


class AlbumStatsResponse(BaseModel):
    """Ответ со статистикой альбома."""
    album_id: int
    total_views: int
    unique_views: int
    avg_duration_seconds: float
    avg_pages_viewed: float
    device_stats: Dict[str, int]
    country_stats: Dict[str, int]
    period: Dict[str, Optional[str]]


class PageStatsResponse(BaseModel):
    """Ответ со статистикой страницы."""
    page_id: int
    total_views: int
    unique_views: int
    avg_duration_seconds: float
    device_stats: Dict[str, int]
    country_stats: Dict[str, int]
    period: Dict[str, Optional[str]]


class DailyStatsResponse(BaseModel):
    """Ответ с ежедневной статистикой."""
    period: Dict[str, str]
    daily_scans: Dict[str, int]
    daily_page_views: Dict[str, int]
    daily_album_views: Dict[str, int]


class TopContentResponse(BaseModel):
    """Ответ с топ контентом."""
    content_type: str
    items: List[Dict[str, Any]]


@router.get("/stats/qr-code/{qr_code_id}", response_model=QRCodeStatsResponse)
async def get_qr_code_stats(
    qr_code_id: int,
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики по QR коду."""
    stats_service = StatsService(db)
    
    try:
        stats = await stats_service.get_qr_code_stats(
            qr_code_id=qr_code_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return QRCodeStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики QR кода: {str(e)}"
        )


@router.get("/stats/user/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: int,
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики пользователя."""
    stats_service = StatsService(db)
    
    try:
        stats = await stats_service.get_user_stats(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return UserStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики пользователя: {str(e)}"
        )


@router.get("/stats/album/{album_id}", response_model=AlbumStatsResponse)
async def get_album_stats(
    album_id: int,
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики альбома."""
    stats_service = StatsService(db)
    
    try:
        stats = await stats_service.get_album_stats(
            album_id=album_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return AlbumStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики альбома: {str(e)}"
        )


@router.get("/stats/page/{page_id}", response_model=PageStatsResponse)
async def get_page_stats(
    page_id: int,
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики страницы."""
    stats_service = StatsService(db)
    
    try:
        stats = await stats_service.get_page_stats(
            page_id=page_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return PageStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики страницы: {str(e)}"
        )


@router.get("/stats/daily", response_model=DailyStatsResponse)
async def get_daily_stats(
    start_date: datetime = Query(..., description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
):
    """Получение ежедневной статистики."""
    stats_service = StatsService(db)
    
    try:
        stats = await stats_service.get_daily_stats(
            start_date=start_date,
            end_date=end_date
        )
        
        return DailyStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении ежедневной статистики: {str(e)}"
        )


@router.get("/stats/top-content", response_model=TopContentResponse)
async def get_top_content(
    content_type: str = Query("albums", description="Тип контента (albums или pages)"),
    limit: int = Query(10, ge=1, le=100, description="Количество записей"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
):
    """Получение топ контента."""
    stats_service = StatsService(db)
    
    if content_type not in ["albums", "pages"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content_type должен быть 'albums' или 'pages'"
        )
    
    try:
        top_content = await stats_service.get_top_content(
            content_type=content_type,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
        
        return TopContentResponse(
            content_type=content_type,
            items=top_content
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении топ контента: {str(e)}"
        )


@router.get("/stats/overview")
async def get_overview_stats(
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db)
):
    """Получение общей статистики системы."""
    stats_service = StatsService(db)
    
    try:
        # Если даты не указаны, берем последние 30 дней
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Получаем ежедневную статистику
        daily_stats = await stats_service.get_daily_stats(start_date, end_date)
        
        # Получаем топ альбомы
        top_albums = await stats_service.get_top_content("albums", 5, start_date, end_date)
        
        # Получаем топ страницы
        top_pages = await stats_service.get_top_content("pages", 5, start_date, end_date)
        
        # Подсчитываем общие метрики
        total_scans = sum(daily_stats["daily_scans"].values())
        total_page_views = sum(daily_stats["daily_page_views"].values())
        total_album_views = sum(daily_stats["daily_album_views"].values())
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_scans": total_scans,
                "total_page_views": total_page_views,
                "total_album_views": total_album_views
            },
            "daily_stats": daily_stats,
            "top_albums": top_albums,
            "top_pages": top_pages
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении общей статистики: {str(e)}"
        )


@router.get("/overview")
async def get_overview(
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """Получение общей статистики системы (алиас для /stats/overview)."""
    # Перенаправляем на существующий endpoint
    return await get_overview_stats(start_date, end_date, db)