"""
Роуты для работы с модерацией контента.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.moderation_service import ModerationService
from app.models.moderation import ContentType, ModerationType, ModerationStatus

router = APIRouter()


class CreateModerationRequest(BaseModel):
    """Запрос на создание модерации."""
    content_type: ContentType = Field(..., description="Тип контента")
    content_id: Optional[str] = Field(None, description="ID контента")
    content_url: Optional[str] = Field(None, description="URL контента")
    content_text: Optional[str] = Field(None, description="Текстовое содержимое")
    content_metadata: Optional[Dict[str, Any]] = Field(None, description="Метаданные контента")
    moderation_type: ModerationType = Field(default=ModerationType.AUTOMATIC, description="Тип модерации")
    priority: int = Field(default=1, ge=1, le=5, description="Приоритет (1-5)")
    context: Optional[str] = Field(None, description="Контекст запроса")
    source: Optional[str] = Field(None, description="Источник запроса")


class ProcessModerationRequest(BaseModel):
    """Запрос на обработку модерации."""
    moderator_id: Optional[int] = Field(None, description="ID модератора")


class ModerationRequestResponse(BaseModel):
    """Ответ с информацией о запросе на модерацию."""
    id: int
    user_id: int
    content_type: str
    content_id: Optional[str]
    content_url: Optional[str]
    content_text: Optional[str]
    content_metadata: Optional[Dict[str, Any]]
    moderation_type: str
    priority: int
    status: str
    ai_confidence: Optional[float]
    context: Optional[str]
    source: Optional[str]
    created_at: str
    updated_at: str
    processed_at: Optional[str]


class ModerationResultResponse(BaseModel):
    """Ответ с результатом модерации."""
    id: int
    request_id: int
    is_approved: bool
    confidence_score: Optional[float]
    risk_score: Optional[float]
    violations: Optional[Dict[str, Any]]
    violation_categories: Optional[List[str]]
    severity_level: Optional[str]
    ai_model: Optional[str]
    ai_version: Optional[str]
    ai_analysis: Optional[Dict[str, Any]]
    moderator_id: Optional[int]
    moderator_notes: Optional[str]
    human_override: bool
    processing_time_ms: Optional[int]
    created_at: str


class ModerationStatsResponse(BaseModel):
    """Ответ со статистикой модерации."""
    total_requests: int
    requests_by_status: Dict[str, int]
    requests_by_content_type: Dict[str, int]
    requests_by_moderation_type: Dict[str, int]
    ai_stats: Dict[str, Any]


@router.post("/moderation/requests", response_model=ModerationRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_moderation_request(
    request: CreateModerationRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание запроса на модерацию."""
    moderation_service = ModerationService(db)
    
    try:
        moderation_request = await moderation_service.create_moderation_request(
            user_id=user_id,
            content_type=request.content_type,
            content_id=request.content_id,
            content_url=request.content_url,
            content_text=request.content_text,
            content_metadata=request.content_metadata,
            moderation_type=request.moderation_type,
            priority=request.priority,
            context=request.context,
            source=request.source
        )
        
        return ModerationRequestResponse(**moderation_request.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании запроса на модерацию: {str(e)}"
        )


@router.get("/moderation/requests", response_model=List[ModerationRequestResponse])
async def get_my_moderation_requests(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    content_type: Optional[ContentType] = Query(None, description="Тип контента для фильтрации"),
    status: Optional[ModerationStatus] = Query(None, description="Статус для фильтрации"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение запросов на модерацию пользователя."""
    moderation_service = ModerationService(db)
    
    try:
        requests = await moderation_service.get_user_moderation_requests(
            user_id=user_id,
            content_type=content_type,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [ModerationRequestResponse(**request.to_dict()) for request in requests]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении запросов на модерацию: {str(e)}"
        )


@router.get("/moderation/requests/{request_id}", response_model=ModerationRequestResponse)
async def get_moderation_request(
    request_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение запроса на модерацию по ID."""
    moderation_service = ModerationService(db)
    
    request = await moderation_service.get_moderation_request(request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрос на модерацию не найден"
        )
    
    # Проверяем, что запрос принадлежит пользователю
    if request.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    return ModerationRequestResponse(**request.to_dict())


@router.post("/moderation/requests/{request_id}/process", response_model=ModerationResultResponse)
async def process_moderation_request(
    request_id: int,
    request: ProcessModerationRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обработка запроса на модерацию."""
    moderation_service = ModerationService(db)
    
    # Проверяем, что запрос принадлежит пользователю
    moderation_request = await moderation_service.get_moderation_request(request_id)
    if not moderation_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запрос на модерацию не найден"
        )
    
    if moderation_request.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        result = await moderation_service.process_moderation_request(
            request_id=request_id,
            moderator_id=request.moderator_id
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при обработке запроса на модерацию"
            )
        
        return ModerationResultResponse(**result.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке запроса на модерацию: {str(e)}"
        )


@router.get("/moderation/pending", response_model=List[ModerationRequestResponse])
async def get_pending_moderation_requests(
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение запросов, ожидающих обработки."""
    moderation_service = ModerationService(db)
    
    try:
        requests = await moderation_service.get_pending_requests(limit=limit)
        return [ModerationRequestResponse(**request.to_dict()) for request in requests]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении ожидающих запросов: {str(e)}"
        )


@router.get("/moderation/stats", response_model=ModerationStatsResponse)
async def get_moderation_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики модерации."""
    moderation_service = ModerationService(db)
    
    try:
        stats = await moderation_service.get_moderation_stats()
        return ModerationStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики модерации: {str(e)}"
        )