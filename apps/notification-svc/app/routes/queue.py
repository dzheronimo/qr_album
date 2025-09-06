"""
Роуты для работы с очередью уведомлений.
"""

from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.queue_service import QueueService
from app.models.notification import NotificationPriority

router = APIRouter()


class AddToQueueRequest(BaseModel):
    """Запрос на добавление уведомления в очередь."""
    notification_id: int = Field(..., description="ID уведомления")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="Приоритет уведомления")
    scheduled_at: Optional[str] = Field(None, description="Время отправки (ISO format)")
    max_attempts: int = Field(default=3, ge=1, le=10, description="Максимальное количество попыток")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class QueueItemResponse(BaseModel):
    """Ответ с информацией об элементе очереди."""
    id: int
    notification_id: int
    notification: Optional[Dict[str, Any]]
    priority: str
    scheduled_at: str
    attempts: int
    max_attempts: int
    is_processing: bool
    processed_at: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class ProcessQueueResponse(BaseModel):
    """Ответ с результатом обработки очереди."""
    processed: int
    successful: int
    failed: int
    errors: List[str]


class QueueStatsResponse(BaseModel):
    """Ответ со статистикой очереди."""
    total_items: int
    processing_items: int
    ready_items: int
    failed_items: int
    items_by_priority: Dict[str, int]


@router.post("/queue", response_model=QueueItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_queue(
    request: AddToQueueRequest,
    db: AsyncSession = Depends(get_db)
):
    """Добавление уведомления в очередь."""
    queue_service = QueueService(db)
    
    try:
        from datetime import datetime
        
        scheduled_at = None
        if request.scheduled_at:
            scheduled_at = datetime.fromisoformat(request.scheduled_at.replace('Z', '+00:00'))
        
        queue_item = await queue_service.add_to_queue(
            notification_id=request.notification_id,
            priority=request.priority,
            scheduled_at=scheduled_at,
            max_attempts=request.max_attempts,
            extra_data=request.extra_data
        )
        
        return QueueItemResponse(**queue_item.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении в очередь: {str(e)}"
        )


@router.get("/queue", response_model=List[QueueItemResponse])
async def get_pending_queue_items(
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение элементов очереди, готовых к обработке."""
    queue_service = QueueService(db)
    
    try:
        queue_items = await queue_service.get_pending_queue_items(limit=limit)
        return [QueueItemResponse(**item.to_dict()) for item in queue_items]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении элементов очереди: {str(e)}"
        )


@router.get("/queue/{queue_id}", response_model=QueueItemResponse)
async def get_queue_item(
    queue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение элемента очереди по ID."""
    queue_service = QueueService(db)
    
    queue_item = await queue_service.get_queue_item_by_id(queue_id)
    if not queue_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Элемент очереди не найден"
        )
    
    return QueueItemResponse(**queue_item.to_dict())


@router.post("/queue/{queue_id}/process", status_code=status.HTTP_200_OK)
async def process_queue_item(
    queue_id: int,
    success: bool = Query(True, description="Успешность обработки"),
    error_message: Optional[str] = Query(None, description="Сообщение об ошибке"),
    db: AsyncSession = Depends(get_db)
):
    """Обработка элемента очереди."""
    queue_service = QueueService(db)
    
    try:
        result = await queue_service.mark_as_processed(
            queue_id=queue_id,
            success=success,
            error_message=error_message
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Элемент очереди не найден"
            )
        
        return {"message": "Элемент очереди обработан"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке элемента очереди: {str(e)}"
        )


@router.delete("/queue/{queue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_queue(
    queue_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление элемента из очереди."""
    queue_service = QueueService(db)
    
    try:
        success = await queue_service.remove_from_queue(queue_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Элемент очереди не найден"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении элемента очереди: {str(e)}"
        )


@router.post("/queue/process-batch", response_model=ProcessQueueResponse)
async def process_queue_batch(
    batch_size: int = Query(10, ge=1, le=100, description="Размер пакета"),
    db: AsyncSession = Depends(get_db)
):
    """Обработка пакета элементов очереди."""
    queue_service = QueueService(db)
    
    try:
        result = await queue_service.process_queue_batch(batch_size=batch_size)
        return ProcessQueueResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке пакета очереди: {str(e)}"
        )


@router.delete("/queue/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_old_queue_items(
    days: int = Query(7, ge=1, le=30, description="Количество дней для очистки"),
    db: AsyncSession = Depends(get_db)
):
    """Очистка старых элементов очереди."""
    queue_service = QueueService(db)
    
    try:
        deleted_count = await queue_service.clear_old_queue_items(days=days)
        return {
            "message": f"Удалено {deleted_count} старых элементов очереди",
            "deleted_count": deleted_count
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при очистке очереди: {str(e)}"
        )


@router.get("/queue/stats", response_model=QueueStatsResponse)
async def get_queue_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики очереди."""
    queue_service = QueueService(db)
    
    try:
        stats = await queue_service.get_queue_stats()
        return QueueStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики очереди: {str(e)}"
        )
