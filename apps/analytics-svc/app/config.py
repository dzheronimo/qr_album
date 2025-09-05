"""
Конфигурация для Analytics сервиса.

Содержит настройки для Analytics сервиса, включая подключение к базе данных.
"""

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """
    Настройки для Analytics сервиса.
    
    Расширяет настройки базы данных специфичными для Analytics сервиса параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения
    
    # Database name for Analytics service
    db_name: str = Field(default="analyticsdb", description="Имя базы данных для Analytics сервиса")