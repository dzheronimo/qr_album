"""
Основной модуль Scan Gateway сервиса.

Содержит FastAPI приложение и настройку маршрутов для Scan Gateway.
"""

from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import Settings
from app.routes import health, redirect

settings = Settings()

# Настройка rate limiter для всего приложения
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)

app = FastAPI(
    title="Scan Gateway",
    description="Gateway для обработки сканирования QR кодов",
    version="1.0.0",
)

# Добавление rate limiter к приложению
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Подключение маршрутов
app.include_router(health.router, tags=["health"])
app.include_router(redirect.router, tags=["redirect"])