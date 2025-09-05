"""
Утилиты для работы с паролями.

Содержит функции для хеширования и проверки паролей.
"""

import secrets
from passlib.context import CryptContext

# Контекст для работы с паролями
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля.
    
    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хешированный пароль
        
    Returns:
        bool: True если пароль верный, False иначе
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля.
    
    Args:
        password: Пароль в открытом виде
        
    Returns:
        str: Хешированный пароль
    """
    return pwd_context.hash(password)


def generate_random_password(length: int = 12) -> str:
    """
    Генерация случайного пароля.
    
    Args:
        length: Длина пароля
        
    Returns:
        str: Случайный пароль
    """
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Проверка силы пароля.
    
    Args:
        password: Пароль для проверки
        
    Returns:
        tuple[bool, list[str]]: (валидный, список ошибок)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Пароль должен содержать минимум 8 символов")
    
    if not any(c.islower() for c in password):
        errors.append("Пароль должен содержать минимум одну строчную букву")
    
    if not any(c.isupper() for c in password):
        errors.append("Пароль должен содержать минимум одну заглавную букву")
    
    if not any(c.isdigit() for c in password):
        errors.append("Пароль должен содержать минимум одну цифру")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Пароль должен содержать минимум один специальный символ")
    
    return len(errors) == 0, errors
