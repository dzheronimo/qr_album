"""
Маршруты для проверки здоровья Scan Gateway сервиса.

Содержит эндпоинты для health checks и мониторинга состояния сервиса.
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel

# Импортируем общие health utilities
import sys
sys.path.append('/app/packages/py-commons')
from health import create_health_router, check_redis, check_http_service

router = APIRouter()

# Создаём health router с проверками зависимостей
health_router = create_health_router("scan-gateway", "1.0.0")

# Добавляем проверки зависимостей
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")

# Получаем health_checker из глобального состояния
from health import _health_checker
if _health_checker:
    _health_checker.add_dependency_check(lambda: check_redis(redis_url))
    
    # Добавляем проверку qr-svc (критичная зависимость)
    qr_svc_url = os.getenv("QR_SVC_URL", "http://qr-svc:8000")
    _health_checker.add_dependency_check(lambda: check_http_service(f"{qr_svc_url}/health", "qr-svc"))
    
    # Добавляем неблокирующую проверку analytics-svc
    analytics_svc_url = os.getenv("ANALYTICS_SVC_URL", "http://analytics-svc:8000")
    _health_checker.add_dependency_check(lambda: check_http_service(f"{analytics_svc_url}/health", "analytics-svc"))

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
