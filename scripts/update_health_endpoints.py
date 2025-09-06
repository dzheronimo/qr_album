#!/usr/bin/env python3
"""
Скрипт для массового обновления health endpoints во всех микросервисах.
"""

import os
import re
from pathlib import Path

# Конфигурация сервисов
SERVICES = {
    "album-svc": {
        "database": "storyqr_album",
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "analytics-svc": {
        "database": "storyqr_analytics", 
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "billing-svc": {
        "database": "storyqr_billing",
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "media-svc": {
        "database": "storyqr_media",
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "moderation-svc": {
        "database": "storyqr_moderation",
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "notification-svc": {
        "database": "storyqr_notification",
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "print-svc": {
        "database": "storyqr_print",
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "qr-svc": {
        "database": "storyqr_qr",
        "dependencies": ["database", "redis", "rabbitmq"]
    },
    "scan-gateway": {
        "database": None,
        "dependencies": ["redis"]
    },
    "user-profile-svc": {
        "database": "storyqr_user_profile",
        "dependencies": ["database", "redis", "rabbitmq"]
    }
}

def update_health_file(service_name: str, service_config: dict):
    """Обновляет health.py файл для сервиса."""
    health_file = Path(f"apps/{service_name}/app/routes/health.py")
    
    if not health_file.exists():
        print(f"Health file not found for {service_name}")
        return
    
    # Читаем текущий файл
    with open(health_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Создаём новый контент
    new_content = f'''"""
Маршруты для проверки здоровья {service_name.replace('-', ' ').title()} сервиса.

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
health_router = create_health_router("{service_name}", "1.0.0")

# Добавляем проверки зависимостей'''
    
    # Добавляем проверки зависимостей
    if service_config["database"]:
        new_content += f'''
database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://storyqr:storyqr@postgres:5432/{service_config['database']}")
health_checker = health_router.dependency_overrides.get("health_checker")
if health_checker:
    health_checker.add_dependency_check(lambda: check_database(database_url))'''
    
    if "redis" in service_config["dependencies"]:
        new_content += '''
redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
if health_checker:
    health_checker.add_dependency_check(lambda: check_redis(redis_url))'''
    
    if "rabbitmq" in service_config["dependencies"]:
        new_content += '''
rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbit:5672")
if health_checker:
    health_checker.add_dependency_check(lambda: check_rabbitmq(rabbitmq_url))'''
    
    new_content += '''

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
'''
    
    # Записываем новый файл
    with open(health_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated health endpoints for {service_name}")

def main():
    """Основная функция."""
    print("Updating health endpoints for all services...")
    
    for service_name, service_config in SERVICES.items():
        try:
            update_health_file(service_name, service_config)
        except Exception as e:
            print(f"Error updating {service_name}: {e}")
    
    print("Health endpoints update completed!")

if __name__ == "__main__":
    main()
