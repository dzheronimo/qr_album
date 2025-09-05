"""
Роуты для работы с печатью и PDF генерацией.
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.print_service import PrintService
from app.models.print_models import PrintJobType, PrintFormat, PrintJobStatus

router = APIRouter()


class CreatePrintJobRequest(BaseModel):
    """Запрос на создание задания печати."""
    job_type: PrintJobType = Field(..., description="Тип задания печати")
    content_data: Dict[str, Any] = Field(..., description="Данные контента для печати")
    template_id: Optional[int] = Field(None, description="ID шаблона")
    layout_id: Optional[int] = Field(None, description="ID макета")
    print_format: PrintFormat = Field(default=PrintFormat.PDF, description="Формат печати")
    page_size: str = Field(default="A4", description="Размер страницы")
    orientation: str = Field(default="portrait", description="Ориентация страницы")
    quality: int = Field(default=300, ge=72, le=600, description="Качество (DPI)")
    priority: int = Field(default=1, ge=1, le=5, description="Приоритет (1-5)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")


class ProcessPrintJobRequest(BaseModel):
    """Запрос на обработку задания печати."""
    worker_id: Optional[str] = Field(None, description="ID воркера")


class PrintJobResponse(BaseModel):
    """Ответ с информацией о задании печати."""
    id: int
    user_id: int
    job_type: str
    template_id: Optional[int]
    layout_id: Optional[int]
    content_data: Dict[str, Any]
    print_format: str
    page_size: str
    orientation: str
    quality: int
    status: str
    progress: int
    output_file_path: Optional[str]
    output_file_size: Optional[int]
    output_url: Optional[str]
    error_message: Optional[str]
    error_details: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    priority: int
    created_at: str
    updated_at: str
    started_at: Optional[str]
    completed_at: Optional[str]


class PrintStatsResponse(BaseModel):
    """Ответ со статистикой печати."""
    total_jobs: int
    jobs_by_status: Dict[str, int]
    jobs_by_type: Dict[str, int]
    jobs_by_format: Dict[str, int]


@router.post("/print/jobs", response_model=PrintJobResponse, status_code=status.HTTP_201_CREATED)
async def create_print_job(
    request: CreatePrintJobRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание задания печати."""
    print_service = PrintService(db)
    
    try:
        print_job = await print_service.create_print_job(
            user_id=user_id,
            job_type=request.job_type,
            content_data=request.content_data,
            template_id=request.template_id,
            layout_id=request.layout_id,
            print_format=request.print_format,
            page_size=request.page_size,
            orientation=request.orientation,
            quality=request.quality,
            priority=request.priority,
            metadata=request.metadata
        )
        
        return PrintJobResponse(**print_job.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании задания печати: {str(e)}"
        )


@router.get("/print/jobs", response_model=List[PrintJobResponse])
async def get_my_print_jobs(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    job_type: Optional[PrintJobType] = Query(None, description="Тип задания для фильтрации"),
    status: Optional[PrintJobStatus] = Query(None, description="Статус для фильтрации"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение заданий печати пользователя."""
    print_service = PrintService(db)
    
    try:
        jobs = await print_service.get_user_print_jobs(
            user_id=user_id,
            job_type=job_type,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [PrintJobResponse(**job.to_dict()) for job in jobs]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении заданий печати: {str(e)}"
        )


@router.get("/print/jobs/{job_id}", response_model=PrintJobResponse)
async def get_print_job(
    job_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение задания печати по ID."""
    print_service = PrintService(db)
    
    job = await print_service.get_print_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание печати не найдено"
        )
    
    # Проверяем, что задание принадлежит пользователю
    if job.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    return PrintJobResponse(**job.to_dict())


@router.post("/print/jobs/{job_id}/process", status_code=status.HTTP_200_OK)
async def process_print_job(
    job_id: int,
    request: ProcessPrintJobRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обработка задания печати."""
    print_service = PrintService(db)
    
    # Проверяем, что задание принадлежит пользователю
    job = await print_service.get_print_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание печати не найдено"
        )
    
    if job.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        success = await print_service.process_print_job(
            job_id=job_id,
            worker_id=request.worker_id
        )
        
        if success:
            return {"message": "Задание печати успешно обработано", "success": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при обработке задания печати"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке задания печати: {str(e)}"
        )


@router.get("/print/jobs/{job_id}/download", status_code=status.HTTP_200_OK)
async def download_print_job_result(
    job_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Скачивание результата задания печати."""
    print_service = PrintService(db)
    
    job = await print_service.get_print_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задание печати не найдено"
        )
    
    # Проверяем, что задание принадлежит пользователю
    if job.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    if job.status != PrintJobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Задание печати еще не завершено"
        )
    
    if not job.output_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл результата не найден"
        )
    
    # В реальном приложении здесь была бы логика скачивания файла
    return {
        "download_url": job.output_url or f"/api/v1/print/jobs/{job_id}/file",
        "file_path": job.output_file_path,
        "file_size": job.output_file_size,
        "format": job.print_format.value
    }


@router.get("/print/stats", response_model=PrintStatsResponse)
async def get_print_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики печати."""
    print_service = PrintService(db)
    
    try:
        stats = await print_service.get_print_stats()
        return PrintStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики печати: {str(e)}"
        )
