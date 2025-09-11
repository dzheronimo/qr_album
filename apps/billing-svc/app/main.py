"""
Основной модуль Billing сервиса.

Содержит FastAPI приложение и настройку маршрутов для Billing сервиса.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.routes import (
    health_router,
    subscriptions_router,
    payments_router,
    plans_router,
    usage_router,
    limits_router
)
from app.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация
    await init_db()
    yield
    # Очистка
    await close_db()


app = FastAPI(
    title="Billing Service",
    description="Сервис для управления биллингом и подписками",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение маршрутов
app.include_router(health_router, tags=["health"])
app.include_router(subscriptions_router, tags=["subscriptions"])
app.include_router(payments_router, tags=["payments"])
app.include_router(plans_router, tags=["plans"])
app.include_router(usage_router, tags=["usage"])
app.include_router(limits_router, tags=["limits"])