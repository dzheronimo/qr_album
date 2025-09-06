"""
Основной файл приложения Moderation сервиса.

Содержит настройки FastAPI приложения и подключение роутов.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.database import init_db, close_db
from app.routes import (
    health_router,
    moderation_router,
    rules_router,
    logs_router,
    ai_router
)

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация при запуске
    await init_db()
    yield
    # Очистка при завершении
    await close_db()


# Создание FastAPI приложения
app = FastAPI(
    title="Moderation Service",
    description="Сервис для модерации контента с AI интеграцией",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(health_router, tags=["health"])  # Health без префикса
app.include_router(moderation_router, prefix="/api/v1", tags=["moderation"])
app.include_router(rules_router, prefix="/api/v1", tags=["rules"])
app.include_router(logs_router, prefix="/api/v1", tags=["logs"])
app.include_router(ai_router, prefix="/api/v1", tags=["ai"])


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Moderation Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }