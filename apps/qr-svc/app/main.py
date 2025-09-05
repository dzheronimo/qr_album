"""
Основной модуль QR сервиса.

Содержит FastAPI приложение и настройку маршрутов для QR сервиса.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db, close_db
from app.routes import health, qr_codes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения.
    
    Инициализирует базу данных при запуске приложения.
    """
    # Инициализация базы данных
    await init_db()
    yield
    # Закрытие соединений
    await close_db()


app = FastAPI(
    title="QR Service",
    description="Сервис для создания QR кодов и коротких ссылок",
    version="1.0.0",
    lifespan=lifespan,
)

# Подключение маршрутов
app.include_router(health.router, tags=["health"])
app.include_router(qr_codes.router, tags=["qr-codes"])