"""
Роуты для проверки состояния сервиса.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Проверка состояния сервиса."""
    return {
        "status": "healthy",
        "service": "notification-svc",
        "version": "1.0.0"
    }


@router.get("/health/db", status_code=status.HTTP_200_OK)
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """Проверка состояния базы данных."""
    try:
        # Простой запрос для проверки подключения к БД
        await db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }