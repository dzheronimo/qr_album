"""
Маршруты для работы с профилями пользователей.

Содержит эндпоинты для получения информации о профилях пользователей.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class UserProfile(BaseModel):
    """Модель профиля пользователя."""
    user_id: str
    tier: str


@router.get("/profile", response_model=UserProfile)
async def get_profile() -> UserProfile:
    """
    Получение профиля пользователя.
    
    Returns:
        UserProfile: Профиль пользователя
    """
    return UserProfile(
        user_id="u_1",
        tier="FREE"
    )