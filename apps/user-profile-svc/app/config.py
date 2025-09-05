"""
Конфигурация для User Profile сервиса.

Содержит настройки для User Profile сервиса, включая подключение к базе данных.
"""

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """
    Настройки для User Profile сервиса.
    
    Расширяет настройки базы данных специфичными для User Profile сервиса параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения
    
    # Database name for User Profile service
    db_name: str = Field(default="profiledb", description="Имя базы данных для User Profile сервиса")