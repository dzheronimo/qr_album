"""
Утилиты для работы с токенами.

Содержит функции для генерации токенов верификации и восстановления пароля.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional


def generate_verification_token() -> str:
    """
    Генерация токена для верификации email.
    
    Returns:
        str: Случайный токен
    """
    return secrets.token_urlsafe(32)


def generate_reset_token() -> str:
    """
    Генерация токена для восстановления пароля.
    
    Returns:
        str: Случайный токен
    """
    return secrets.token_urlsafe(32)


def get_token_expiry(minutes: int = 60) -> datetime:
    """
    Получение времени истечения токена.
    
    Args:
        minutes: Количество минут до истечения
        
    Returns:
        datetime: Время истечения токена
    """
    return datetime.utcnow() + timedelta(minutes=minutes)


def is_token_expired(expires_at: Optional[datetime]) -> bool:
    """
    Проверка истечения токена.
    
    Args:
        expires_at: Время истечения токена
        
    Returns:
        bool: True если токен истек, False иначе
    """
    if expires_at is None:
        return True
    return datetime.utcnow() > expires_at
