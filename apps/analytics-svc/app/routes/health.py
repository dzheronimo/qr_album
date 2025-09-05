"""
Маршруты для проверки здоровья Analytics сервиса.

Содержит эндпоинты для health checks и мониторинга состояния сервиса.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Модель ответа для health check."""
    ok: bool


@router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Проверка здоровья Analytics сервиса.
    
    Returns:
        HealthResponse: Статус здоровья сервиса
    """
    return HealthResponse(ok=True)