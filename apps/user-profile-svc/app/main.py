"""
Основной модуль User Profile сервиса.

Содержит FastAPI приложение и настройку маршрутов для User Profile сервиса.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routes import health, profiles, settings
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
    title="User Profile Service",
    description="Сервис для управления профилями пользователей",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение маршрутов
app.include_router(health.router, tags=["health"])
app.include_router(profiles.router, tags=["profiles"])
app.include_router(settings.router, tags=["settings"])