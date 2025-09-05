"""
Роуты для работы с подписками.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.subscription_service import SubscriptionService
from app.models.billing import SubscriptionStatus

router = APIRouter()


class CreateSubscriptionRequest(BaseModel):
    """Запрос на создание подписки."""
    plan_id: int = Field(..., description="ID тарифного плана")
    billing_cycle: str = Field(default="monthly", description="Цикл биллинга (monthly, yearly)")
    auto_renew: bool = Field(default=True, description="Автопродление")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class UpdateSubscriptionRequest(BaseModel):
    """Запрос на обновление подписки."""
    status: Optional[SubscriptionStatus] = Field(None, description="Статус подписки")
    auto_renew: Optional[bool] = Field(None, description="Автопродление")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class SubscriptionResponse(BaseModel):
    """Ответ с информацией о подписке."""
    id: int
    user_id: int
    plan_id: int
    plan: Optional[Dict[str, Any]]
    status: str
    billing_cycle: str
    start_date: str
    end_date: Optional[str]
    next_billing_date: Optional[str]
    cancelled_at: Optional[str]
    auto_renew: bool
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class SubscriptionStatsResponse(BaseModel):
    """Ответ со статистикой подписок."""
    user_id: int
    total_subscriptions: int
    active_subscriptions: int
    current_subscription: Optional[Dict[str, Any]]


@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: CreateSubscriptionRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание подписки пользователя."""
    subscription_service = SubscriptionService(db)
    
    try:
        subscription = await subscription_service.create_subscription(
            user_id=user_id,
            plan_id=request.plan_id,
            billing_cycle=request.billing_cycle,
            auto_renew=request.auto_renew,
            extra_data=request.extra_data
        )
        
        return SubscriptionResponse(**subscription.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании подписки: {str(e)}"
        )


@router.get("/subscriptions/me", response_model=Optional[SubscriptionResponse])
async def get_my_subscription(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение активной подписки пользователя."""
    subscription_service = SubscriptionService(db)
    
    subscription = await subscription_service.get_active_subscription(user_id)
    if not subscription:
        return None
    
    return SubscriptionResponse(**subscription.to_dict())


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_my_subscriptions(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех подписок пользователя."""
    subscription_service = SubscriptionService(db)
    
    try:
        subscriptions = await subscription_service.get_user_subscriptions(
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        return [SubscriptionResponse(**subscription.to_dict()) for subscription in subscriptions]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении подписок: {str(e)}"
        )


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение подписки по ID."""
    subscription_service = SubscriptionService(db)
    
    subscription = await subscription_service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )
    
    # Проверяем, что подписка принадлежит пользователю
    if subscription.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    return SubscriptionResponse(**subscription.to_dict())


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    request: UpdateSubscriptionRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление подписки."""
    subscription_service = SubscriptionService(db)
    
    # Проверяем, что подписка принадлежит пользователю
    subscription = await subscription_service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )
    
    if subscription.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        updated_subscription = await subscription_service.update_subscription(
            subscription_id=subscription_id,
            status=request.status,
            auto_renew=request.auto_renew,
            extra_data=request.extra_data
        )
        
        if not updated_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подписка не найдена"
            )
        
        return SubscriptionResponse(**updated_subscription.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении подписки: {str(e)}"
        )


@router.post("/subscriptions/{subscription_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_subscription(
    subscription_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Отмена подписки."""
    subscription_service = SubscriptionService(db)
    
    # Проверяем, что подписка принадлежит пользователю
    subscription = await subscription_service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )
    
    if subscription.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        success = await subscription_service.cancel_subscription(subscription_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подписка не найдена"
            )
        
        return {"message": "Подписка успешно отменена"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отмене подписки: {str(e)}"
        )


@router.post("/subscriptions/{subscription_id}/renew", status_code=status.HTTP_200_OK)
async def renew_subscription(
    subscription_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Продление подписки."""
    subscription_service = SubscriptionService(db)
    
    # Проверяем, что подписка принадлежит пользователю
    subscription = await subscription_service.get_subscription_by_id(subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка не найдена"
        )
    
    if subscription.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        success = await subscription_service.renew_subscription(subscription_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Подписка не найдена"
            )
        
        return {"message": "Подписка успешно продлена"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при продлении подписки: {str(e)}"
        )


@router.get("/subscriptions/me/stats", response_model=SubscriptionStatsResponse)
async def get_my_subscription_stats(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики подписок пользователя."""
    subscription_service = SubscriptionService(db)
    
    try:
        stats = await subscription_service.get_subscription_stats(user_id)
        return SubscriptionStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики подписок: {str(e)}"
        )
