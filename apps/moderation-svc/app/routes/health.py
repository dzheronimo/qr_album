"""
Маршруты для проверки здоровья Moderation Svc сервиса.

Содержит эндпоинты для health checks и мониторинга состояния сервиса.
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel

# Импортируем общие health utilities
import sys
sys.path.append('/app/packages')
from py_commons.health import create_health_router, check_database, check_redis, check_rabbitmq

router = APIRouter()

# Создаём health router с проверками зависимостей
health_router = create_health_router("moderation-svc", "1.0.0")

# Добавляем проверки зависимостей
database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://storyqr:storyqr@postgres:5432/storyqr_moderation")
health_checker = health_router.dependency_overrides.get("health_checker")
if health_checker:
    health_checker.add_dependency_check(lambda: check_database(database_url))
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
if health_checker:
    health_checker.add_dependency_check(lambda: check_redis(redis_url))
rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbit:5672")
if health_checker:
    health_checker.add_dependency_check(lambda: check_rabbitmq(rabbitmq_url))

# Включаем health endpoints
router.include_router(health_router)

# Оставляем старый endpoint для совместимости
class HealthResponse(BaseModel):
    """Модель ответа для health check."""
    ok: bool


@router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Проверка здоровья {service_name.replace('-', ' ').title()} сервиса (legacy endpoint).
    
    Returns:
        HealthResponse: Статус здоровья сервиса
    """
    return HealthResponse(ok=True)
