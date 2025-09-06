"""
Роуты для работы с лимитами пользователей.

Реализует эндпоинт GET /api/v1/billing/limits согласно контракту API.md.
"""

from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.limits_service import LimitsService
from app.models.limits import LimitsResponseV2

router = APIRouter()


class LimitsCheckRequest(BaseModel):
    """Запрос на проверку лимитов для операции."""
    albums_delta: int = 0
    pages_delta: int = 0
    storage_delta_mb: int = 0


class LimitsCheckResponse(BaseModel):
    """Ответ с результатом проверки лимитов."""
    can_proceed: bool
    exceeded_limits: list[str] = []
    limits: Dict[str, Any] = None
    message: str = None


@router.get("/limits", response_model=LimitsResponseV2)
async def get_limits(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Получение лимитов пользователя.
    
    Возвращает информацию о лимитах в формате API.md:
    {
        "albums": {"used": 3, "limit": 5, "remaining": 2},
        "pages": {"used": 15, "limit": 50, "remaining": 35},
        "storage": {"used_mb": 45, "limit_mb": 100, "remaining_mb": 55}
    }
    """
    limits_service = LimitsService(db)
    
    try:
        limits = await limits_service.get_user_limits(user_id)
        return limits
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении лимитов: {str(e)}"
        )


@router.post("/limits/check", response_model=LimitsCheckResponse)
async def check_limits_for_operation(
    request: LimitsCheckRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Проверка лимитов для выполнения операции.
    
    Проверяет, можно ли выполнить операцию с учетом текущих лимитов.
    """
    limits_service = LimitsService(db)
    
    try:
        result = await limits_service.check_limits_for_operation(
            user_id=user_id,
            albums_delta=request.albums_delta,
            pages_delta=request.pages_delta,
            storage_delta_mb=request.storage_delta_mb
        )
        
        return LimitsCheckResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при проверке лимитов: {str(e)}"
        )
