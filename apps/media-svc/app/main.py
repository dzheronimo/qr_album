"""
Основной модуль Media сервиса.

Содержит FastAPI приложение и настройку маршрутов для Media сервиса.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routes import health, media
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
    title="Media Service",
    description="Сервис для работы с медиафайлами",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение маршрутов
app.include_router(health.router, tags=["health"])
app.include_router(media.router, tags=["media"])