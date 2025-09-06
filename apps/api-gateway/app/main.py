"""
Основной модуль API Gateway сервиса.

Содержит FastAPI приложение и настройку маршрутов для API Gateway.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware

from app.routes import health, proxy, auth
from app.middleware import AuthMiddleware, RateLimitMiddleware, LoggingMiddleware, CORSMiddleware
from app.config import Settings

settings = Settings()

app = FastAPI(
    title="API Gateway",
    description="API Gateway для QR-Albums",
    version="1.0.0",
)

# Добавляем middleware в правильном порядке
# CORS должен быть первым
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Безопасные домены из конфигурации
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Логирование
app.add_middleware(LoggingMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, requests_per_hour=1000)

# Аутентификация (опциональная для некоторых путей)
app.add_middleware(AuthMiddleware)

# Подключение маршрутов
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, tags=["auth"])
app.include_router(proxy.router, tags=["proxy"])