"""
Конфигурация для Scan Gateway сервиса.

Содержит настройки для Scan Gateway, включая rate limiting,
Redis и другие параметры.
"""

from app.commons.settings import CommonSettings


class Settings(CommonSettings):
    """
    Настройки для Scan Gateway сервиса.
    
    Расширяет базовые настройки специфичными для Scan Gateway параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения