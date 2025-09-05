"""
Роуты для работы с очередью печати.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.queue_service import QueueService

router = APIRouter()


class QueueItemResponse(BaseModel):
    """Ответ с информацией об элементе очереди."""
    id: int
    job_id: int
    priority: int
    scheduled_at: Optional[str]
    is_processing: bool
    worker_id: Optional[str]
    attempts: int
    max_attempts: int
    last_attempt_at: Optional[str]
    created_at: str
    updated_at: str


class QueueStatsResponse(BaseModel):
    """Ответ со статистикой очереди."""
    total_in_queue: int
    processing: int
    waiting: int
    by_priority: Dict[int, int]
    failed: int
    average_wait_time_seconds: float


class RescheduleRequest(BaseModel):
    """Запрос на перенос задания."""
    scheduled_at: datetime = Field(..., description="Новое время выполнения")


class ChangePriorityRequest(BaseModel):
    """Запрос на изменение приоритета."""
    priority: int = Field(..., ge=1, le=5, description="Новый приоритет (1-5)")


@router.get("/queue/status", response_model=QueueStatsResponse)
async def get_queue_status(
    db: AsyncSession = Depends(get_db)
):
    """Получение статуса очереди печати."""
    queue_service = QueueService(db)
    
    try:
        stats = await queue_service.get_queue_stats()
        return QueueStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статуса очереди: {str(e)}"
        )


@router.get("/queue/items", response_model=List[QueueItemResponse])
async def get_queue_items(
    is_processing: Optional[bool] = Query(None, description="Фильтр по статусу обработки"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Фильтр по приоритету"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение элементов очереди печати."""
    queue_service = QueueService(db)
    
    try:
        items = await queue_service.get_queue_items(
            is_processing=is_processing,
            priority=priority,
            skip=skip,
            limit=limit
        )
        
        return [QueueItemResponse(**item.to_dict()) for item in items]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении элементов очереди: {str(e)}"
        )


@router.post("/queue/next", response_model=QueueItemResponse)
async def get_next_job(
    worker_id: str = Query(..., description="ID воркера"),
    max_attempts: int = Query(3, ge=1, le=10, description="Максимальное количество попыток"),
    db: AsyncSession = Depends(get_db)
):
    """Получение следующего задания из очереди."""
    queue_service = QueueService(db)
    
    try:
        queue_item = await queue_service.get_next_job(
            worker_id=worker_id,
            max_attempts=max_attempts
        )
        
        if not queue_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Нет доступных заданий в очереди"
            )
        
        return QueueItemResponse(**queue_item.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении следующего задания: {str(e)}"
        )


@router.post("/queue/jobs/{job_id}/complete", status_code=status.HTTP_200_OK)
async def mark_job_completed(
    job_id: int,
    success: bool = Query(True, description="Успешность выполнения"),
    db: AsyncSession = Depends(get_db)
):
    """Отметка задания как завершенного."""
    queue_service = QueueService(db)
    
    try:
        success_result = await queue_service.mark_job_completed(
            job_id=job_id,
            success=success
        )
        
        if success_result:
            return {"message": "Задание успешно отмечено как завершенное", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при отметке задания как завершенного"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отметке задания: {str(e)}"
        )


@router.post("/queue/jobs/{job_id}/failed", status_code=status.HTTP_200_OK)
async def mark_job_failed(
    job_id: int,
    error_message: Optional[str] = Query(None, description="Сообщение об ошибке"),
    db: AsyncSession = Depends(get_db)
):
    """Отметка задания как неудачного."""
    queue_service = QueueService(db)
    
    try:
        success = await queue_service.mark_job_failed(
            job_id=job_id,
            error_message=error_message
        )
        
        if success:
            return {"message": "Задание отмечено как неудачное", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при отметке задания как неудачного"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отметке задания: {str(e)}"
        )


@router.post("/queue/jobs/{job_id}/reschedule", status_code=status.HTTP_200_OK)
async def reschedule_job(
    job_id: int,
    request: RescheduleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Перенос задания на другое время."""
    queue_service = QueueService(db)
    
    try:
        success = await queue_service.reschedule_job(
            job_id=job_id,
            scheduled_at=request.scheduled_at
        )
        
        if success:
            return {"message": "Задание успешно перенесено", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при переносе задания"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при переносе задания: {str(e)}"
        )


@router.post("/queue/jobs/{job_id}/priority", status_code=status.HTTP_200_OK)
async def change_job_priority(
    job_id: int,
    request: ChangePriorityRequest,
    db: AsyncSession = Depends(get_db)
):
    """Изменение приоритета задания."""
    queue_service = QueueService(db)
    
    try:
        success = await queue_service.change_job_priority(
            job_id=job_id,
            priority=request.priority
        )
        
        if success:
            return {"message": "Приоритет задания успешно изменен", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при изменении приоритета задания"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при изменении приоритета: {str(e)}"
        )


@router.delete("/queue/jobs/{job_id}", status_code=status.HTTP_200_OK)
async def remove_job_from_queue(
    job_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление задания из очереди."""
    queue_service = QueueService(db)
    
    try:
        success = await queue_service.remove_from_queue(job_id)
        
        if success:
            return {"message": "Задание успешно удалено из очереди", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при удалении задания из очереди"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении задания: {str(e)}"
        )


@router.post("/queue/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_old_queue_items(
    hours: int = Query(24, ge=1, le=168, description="Количество часов для хранения"),
    db: AsyncSession = Depends(get_db)
):
    """Очистка старых элементов очереди."""
    queue_service = QueueService(db)
    
    try:
        deleted_count = await queue_service.cleanup_old_queue_items(hours=hours)
        return {
            "message": f"Удалено {deleted_count} старых элементов очереди",
            "deleted_count": deleted_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при очистке очереди: {str(e)}"
        )
