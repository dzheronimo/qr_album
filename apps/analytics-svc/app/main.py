"""
Основной модуль Analytics сервиса.

Содержит FastAPI приложение и настройку маршрутов для Analytics сервиса.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routes import health, analytics, stats
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    
    Инициализирует базу данных при запуске и закрывает соединения при остановке.
    """
    # Инициализация при запуске
    await init_db()
    yield
    # Очистка при остановке
    await close_db()


app = FastAPI(
    title="Analytics Service",
    description="Сервис для аналитики и статистики",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение маршрутов
app.include_router(health.router, tags=["health"])
app.include_router(analytics.router, tags=["analytics"])
app.include_router(stats.router, tags=["stats"])