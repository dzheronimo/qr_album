"""
Роуты для работы с тарифными планами.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.plan_service import PlanService
from app.models.billing import PlanType

router = APIRouter()


class CreatePlanRequest(BaseModel):
    """Запрос на создание тарифного плана."""
    name: str = Field(..., min_length=1, max_length=100, description="Название плана")
    plan_type: PlanType = Field(..., description="Тип плана")
    price_monthly: Decimal = Field(..., ge=0, description="Месячная цена")
    price_yearly: Optional[Decimal] = Field(None, ge=0, description="Годовая цена")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Валюта")
    description: Optional[str] = Field(None, description="Описание плана")
    max_albums: Optional[int] = Field(None, ge=0, description="Максимальное количество альбомов")
    max_pages_per_album: Optional[int] = Field(None, ge=0, description="Максимальное количество страниц в альбоме")
    max_media_files: Optional[int] = Field(None, ge=0, description="Максимальное количество медиафайлов")
    max_qr_codes: Optional[int] = Field(None, ge=0, description="Максимальное количество QR кодов")
    max_storage_gb: Optional[int] = Field(None, ge=0, description="Максимальное хранилище в ГБ")
    features: Optional[Dict[str, Any]] = Field(None, description="Функции плана")
    is_popular: bool = Field(default=False, description="Популярный план")


class UpdatePlanRequest(BaseModel):
    """Запрос на обновление тарифного плана."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название плана")
    plan_type: Optional[PlanType] = Field(None, description="Тип плана")
    price_monthly: Optional[Decimal] = Field(None, ge=0, description="Месячная цена")
    price_yearly: Optional[Decimal] = Field(None, ge=0, description="Годовая цена")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="Валюта")
    description: Optional[str] = Field(None, description="Описание плана")
    max_albums: Optional[int] = Field(None, ge=0, description="Максимальное количество альбомов")
    max_pages_per_album: Optional[int] = Field(None, ge=0, description="Максимальное количество страниц в альбоме")
    max_media_files: Optional[int] = Field(None, ge=0, description="Максимальное количество медиафайлов")
    max_qr_codes: Optional[int] = Field(None, ge=0, description="Максимальное количество QR кодов")
    max_storage_gb: Optional[int] = Field(None, ge=0, description="Максимальное хранилище в ГБ")
    features: Optional[Dict[str, Any]] = Field(None, description="Функции плана")
    is_active: Optional[bool] = Field(None, description="Активный план")
    is_popular: Optional[bool] = Field(None, description="Популярный план")


class PlanResponse(BaseModel):
    """Ответ с информацией о тарифном плане."""
    id: int
    name: str
    plan_type: str
    description: Optional[str]
    price_monthly: float
    price_yearly: Optional[float]
    currency: str
    max_albums: Optional[int]
    max_pages_per_album: Optional[int]
    max_media_files: Optional[int]
    max_qr_codes: Optional[int]
    max_storage_gb: Optional[int]
    features: Optional[Dict[str, Any]]
    is_active: bool
    is_popular: bool
    created_at: str
    updated_at: str


class PlanStatsResponse(BaseModel):
    """Ответ со статистикой планов."""
    total_plans: int
    active_plans: int
    popular_plans: int
    plans_by_type: Dict[str, int]
    top_plans_by_subscriptions: List[Dict[str, Any]]


@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    request: CreatePlanRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание тарифного плана."""
    plan_service = PlanService(db)
    
    try:
        plan = await plan_service.create_plan(
            name=request.name,
            plan_type=request.plan_type,
            price_monthly=request.price_monthly,
            price_yearly=request.price_yearly,
            currency=request.currency,
            description=request.description,
            max_albums=request.max_albums,
            max_pages_per_album=request.max_pages_per_album,
            max_media_files=request.max_media_files,
            max_qr_codes=request.max_qr_codes,
            max_storage_gb=request.max_storage_gb,
            features=request.features,
            is_popular=request.is_popular
        )
        
        return PlanResponse(**plan.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании плана: {str(e)}"
        )


@router.get("/plans", response_model=List[PlanResponse])
async def get_plans(
    plan_type: Optional[PlanType] = Query(None, description="Тип плана для фильтрации"),
    is_active: bool = Query(True, description="Только активные планы"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка тарифных планов."""
    plan_service = PlanService(db)
    
    try:
        plans = await plan_service.get_plans(
            plan_type=plan_type,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        return [PlanResponse(**plan.to_dict()) for plan in plans]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении планов: {str(e)}"
        )


@router.get("/plans/popular", response_model=List[PlanResponse])
async def get_popular_plans(
    db: AsyncSession = Depends(get_db)
):
    """Получение популярных тарифных планов."""
    plan_service = PlanService(db)
    
    try:
        plans = await plan_service.get_popular_plans()
        return [PlanResponse(**plan.to_dict()) for plan in plans]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении популярных планов: {str(e)}"
        )


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение тарифного плана по ID."""
    plan_service = PlanService(db)
    
    plan = await plan_service.get_plan_by_id(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тарифный план не найден"
        )
    
    return PlanResponse(**plan.to_dict())


@router.put("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    request: UpdatePlanRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление тарифного плана."""
    plan_service = PlanService(db)
    
    try:
        updated_plan = await plan_service.update_plan(
            plan_id=plan_id,
            name=request.name,
            plan_type=request.plan_type,
            price_monthly=request.price_monthly,
            price_yearly=request.price_yearly,
            currency=request.currency,
            description=request.description,
            max_albums=request.max_albums,
            max_pages_per_album=request.max_pages_per_album,
            max_media_files=request.max_media_files,
            max_qr_codes=request.max_qr_codes,
            max_storage_gb=request.max_storage_gb,
            features=request.features,
            is_active=request.is_active,
            is_popular=request.is_popular
        )
        
        if not updated_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тарифный план не найден"
            )
        
        return PlanResponse(**updated_plan.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении плана: {str(e)}"
        )


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление тарифного плана."""
    plan_service = PlanService(db)
    
    try:
        success = await plan_service.delete_plan(plan_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тарифный план не найден"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении плана: {str(e)}"
        )


@router.post("/plans/{plan_id}/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Деактивация тарифного плана."""
    plan_service = PlanService(db)
    
    try:
        success = await plan_service.deactivate_plan(plan_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тарифный план не найден"
            )
        
        return {"message": "План успешно деактивирован"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при деактивации плана: {str(e)}"
        )


@router.get("/plans/stats", response_model=PlanStatsResponse)
async def get_plan_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики тарифных планов."""
    plan_service = PlanService(db)
    
    try:
        stats = await plan_service.get_plan_stats()
        return PlanStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики планов: {str(e)}"
        )