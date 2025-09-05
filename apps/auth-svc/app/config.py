"""
Конфигурация для Auth сервиса.

Содержит настройки для Auth сервиса, включая подключение к базе данных.
"""

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """
    Настройки для Auth сервиса.
    
    Расширяет настройки базы данных специфичными для Auth сервиса параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения
    
    # Database name for Auth service
    db_name: str = Field(default="authdb", description="Имя базы данных для Auth сервиса")