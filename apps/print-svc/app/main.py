"""
Основной файл приложения Print сервиса.

Содержит настройки FastAPI приложения и подключение роутов.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings
from app.database import init_db, close_db
from app.routes import (
    health_router,
    print_router,
    templates_router,
    layouts_router,
    queue_router
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
    title="Print Service",
    description="Сервис для генерации PDF и печати QR кодов",
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
app.include_router(print_router, prefix="/api/v1", tags=["print"])
app.include_router(templates_router, prefix="/api/v1", tags=["templates"])
app.include_router(layouts_router, prefix="/api/v1", tags=["layouts"])
app.include_router(queue_router, prefix="/api/v1", tags=["queue"])


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Print Service API",
        "version": "1.0.0",
        "docs": "/docs"
    }