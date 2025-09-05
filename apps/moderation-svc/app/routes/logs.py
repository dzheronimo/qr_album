"""
Роуты для работы с журналом модерации.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.log_service import LogService

router = APIRouter()


class LogResponse(BaseModel):
    """Ответ с информацией о записи журнала."""
    id: int
    request_id: int
    action: str
    actor_type: str
    actor_id: Optional[int]
    details: Optional[Dict[str, Any]]
    message: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    created_at: str


class LogStatsResponse(BaseModel):
    """Ответ со статистикой журнала."""
    total_logs: int
    logs_by_actor_type: Dict[str, int]
    logs_by_action: Dict[str, int]
    daily_activity: List[Dict[str, Any]]
    period_days: int


@router.get("/logs/request/{request_id}", response_model=List[LogResponse])
async def get_logs_by_request(
    request_id: int,
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение записей журнала для запроса."""
    log_service = LogService(db)
    
    try:
        logs = await log_service.get_logs_by_request(
            request_id=request_id,
            skip=skip,
            limit=limit
        )
        
        return [LogResponse(**log.to_dict()) for log in logs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении записей журнала: {str(e)}"
        )


@router.get("/logs/actor/{actor_type}", response_model=List[LogResponse])
async def get_logs_by_actor(
    actor_type: str,
    actor_id: Optional[int] = Query(None, description="ID исполнителя"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение записей журнала по исполнителю."""
    log_service = LogService(db)
    
    try:
        logs = await log_service.get_logs_by_actor(
            actor_type=actor_type,
            actor_id=actor_id,
            skip=skip,
            limit=limit
        )
        
        return [LogResponse(**log.to_dict()) for log in logs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении записей журнала: {str(e)}"
        )


@router.get("/logs/action/{action}", response_model=List[LogResponse])
async def get_logs_by_action(
    action: str,
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение записей журнала по действию."""
    log_service = LogService(db)
    
    try:
        logs = await log_service.get_logs_by_action(
            action=action,
            skip=skip,
            limit=limit
        )
        
        return [LogResponse(**log.to_dict()) for log in logs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении записей журнала: {str(e)}"
        )


@router.get("/logs/recent", response_model=List[LogResponse])
async def get_recent_logs(
    hours: int = Query(24, ge=1, le=168, description="Количество часов назад"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение недавних записей журнала."""
    log_service = LogService(db)
    
    try:
        logs = await log_service.get_recent_logs(
            hours=hours,
            skip=skip,
            limit=limit
        )
        
        return [LogResponse(**log.to_dict()) for log in logs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении недавних записей журнала: {str(e)}"
        )


@router.get("/logs/search", response_model=List[LogResponse])
async def search_logs(
    query_text: Optional[str] = Query(None, description="Текст для поиска"),
    actor_type: Optional[str] = Query(None, description="Тип исполнителя"),
    action: Optional[str] = Query(None, description="Действие"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Поиск записей журнала."""
    log_service = LogService(db)
    
    try:
        logs = await log_service.search_logs(
            query_text=query_text,
            actor_type=actor_type,
            action=action,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
        
        return [LogResponse(**log.to_dict()) for log in logs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при поиске записей журнала: {str(e)}"
        )


@router.get("/logs/stats", response_model=LogStatsResponse)
async def get_log_stats(
    days: int = Query(30, ge=1, le=365, description="Количество дней для анализа"),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики журнала."""
    log_service = LogService(db)
    
    try:
        stats = await log_service.get_log_stats(days=days)
        return LogStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики журнала: {str(e)}"
        )


@router.delete("/logs/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365, description="Количество дней для хранения"),
    db: AsyncSession = Depends(get_db)
):
    """Очистка старых записей журнала."""
    log_service = LogService(db)
    
    try:
        deleted_count = await log_service.cleanup_old_logs(days=days)
        return {
            "message": f"Удалено {deleted_count} старых записей журнала",
            "deleted_count": deleted_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при очистке журнала: {str(e)}"
        )


@router.get("/logs/export", response_model=List[Dict[str, Any]])
async def export_logs(
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    format: str = Query("json", description="Формат экспорта"),
    db: AsyncSession = Depends(get_db)
):
    """Экспорт записей журнала."""
    log_service = LogService(db)
    
    try:
        logs = await log_service.export_logs(
            start_date=start_date,
            end_date=end_date,
            format=format
        )
        
        return logs
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при экспорте журнала: {str(e)}"
        )
