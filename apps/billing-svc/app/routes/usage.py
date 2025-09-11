"""
Роуты для работы с использованием ресурсов.
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.usage_service import UsageService

router = APIRouter()


class UpdateUsageRequest(BaseModel):
    """Запрос на обновление использования ресурсов."""
    albums_count: Optional[int] = Field(None, ge=0, description="Количество альбомов")
    pages_count: Optional[int] = Field(None, ge=0, description="Количество страниц")
    media_files_count: Optional[int] = Field(None, ge=0, description="Количество медиафайлов")
    qr_codes_count: Optional[int] = Field(None, ge=0, description="Количество QR кодов")
    storage_used_mb: Optional[int] = Field(None, ge=0, description="Использованное хранилище в МБ")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class IncrementUsageRequest(BaseModel):
    """Запрос на увеличение использования ресурсов."""
    albums_count: int = Field(default=0, ge=0, description="Увеличение количества альбомов")
    pages_count: int = Field(default=0, ge=0, description="Увеличение количества страниц")
    media_files_count: int = Field(default=0, ge=0, description="Увеличение количества медиафайлов")
    qr_codes_count: int = Field(default=0, ge=0, description="Увеличение количества QR кодов")
    storage_used_mb: int = Field(default=0, ge=0, description="Увеличение используемого хранилища в МБ")


class CheckLimitsRequest(BaseModel):
    """Запрос на проверку лимитов."""
    albums_count: Optional[int] = Field(None, ge=0, description="Количество альбомов для проверки")
    pages_count: Optional[int] = Field(None, ge=0, description="Количество страниц для проверки")
    media_files_count: Optional[int] = Field(None, ge=0, description="Количество медиафайлов для проверки")
    qr_codes_count: Optional[int] = Field(None, ge=0, description="Количество QR кодов для проверки")
    storage_used_mb: Optional[int] = Field(None, ge=0, description="Использованное хранилище в МБ для проверки")
    
    @validator('*', pre=True)
    def validate_positive_values(cls, v):
        """Валидация положительных значений."""
        if v is not None and v < 0:
            raise ValueError('Значение не может быть отрицательным')
        return v


class UsageResponse(BaseModel):
    """Ответ с информацией об использовании ресурсов."""
    id: int
    user_id: int
    albums_count: int
    pages_count: int
    media_files_count: int
    qr_codes_count: int
    storage_used_mb: int
    period_start: str
    period_end: str
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class LimitsCheckResponse(BaseModel):
    """Ответ с результатом проверки лимитов."""
    has_subscription: bool
    plan: Optional[Dict[str, Any]] = None
    current_usage: Optional[Dict[str, Any]] = None
    limits_exceeded: bool
    exceeded_limits: List[str] = []
    can_proceed: bool
    message: Optional[str] = None


class UsageStatsResponse(BaseModel):
    """Ответ со статистикой использования ресурсов."""
    user_id: int
    has_subscription: bool
    plan: Optional[Dict[str, Any]] = None
    current_usage: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None
    usage_percentages: Optional[Dict[str, float]] = None


@router.get("/usage/current", response_model=Optional[UsageResponse])
async def get_current_usage(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение текущего использования ресурсов пользователя."""
    usage_service = UsageService(db)
    
    try:
        usage = await usage_service.get_current_usage(user_id)
        if not usage:
            return None
        
        return UsageResponse(**usage.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении текущего использования: {str(e)}"
        )


@router.put("/usage/current", response_model=UsageResponse)
async def update_current_usage(
    request: UpdateUsageRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление текущего использования ресурсов."""
    usage_service = UsageService(db)
    
    try:
        usage = await usage_service.create_or_update_usage(
            user_id=user_id,
            albums_count=request.albums_count,
            pages_count=request.pages_count,
            media_files_count=request.media_files_count,
            qr_codes_count=request.qr_codes_count,
            storage_used_mb=request.storage_used_mb,
            extra_data=request.extra_data
        )
        
        return UsageResponse(**usage.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении использования: {str(e)}"
        )


@router.post("/usage/increment", response_model=UsageResponse)
async def increment_usage(
    request: IncrementUsageRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Увеличение использования ресурсов."""
    usage_service = UsageService(db)
    
    try:
        usage = await usage_service.increment_usage(
            user_id=user_id,
            albums_count=request.albums_count,
            pages_count=request.pages_count,
            media_files_count=request.media_files_count,
            qr_codes_count=request.qr_codes_count,
            storage_used_mb=request.storage_used_mb
        )
        
        return UsageResponse(**usage.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при увеличении использования: {str(e)}"
        )


@router.post("/usage/check-limits", response_model=LimitsCheckResponse)
async def check_limits(
    request: CheckLimitsRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Проверка лимитов пользователя."""
    usage_service = UsageService(db)
    
    try:
        result = await usage_service.check_limits(
            user_id=user_id,
            albums_count=request.albums_count,
            pages_count=request.pages_count,
            media_files_count=request.media_files_count,
            qr_codes_count=request.qr_codes_count,
            storage_used_mb=request.storage_used_mb
        )
        
        return LimitsCheckResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при проверке лимитов: {str(e)}"
        )


@router.get("/usage/history", response_model=List[UsageResponse])
async def get_usage_history(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(12, ge=1, le=50, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение истории использования ресурсов."""
    usage_service = UsageService(db)
    
    try:
        usage_history = await usage_service.get_usage_history(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        return [UsageResponse(**usage.to_dict()) for usage in usage_history]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории использования: {str(e)}"
        )


@router.get("/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики использования ресурсов."""
    usage_service = UsageService(db)
    
    try:
        stats = await usage_service.get_usage_stats(user_id)
        return UsageStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики использования: {str(e)}"
        )
