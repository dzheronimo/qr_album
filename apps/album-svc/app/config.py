"""
Конфигурация для Album сервиса.

Содержит настройки для Album сервиса, включая подключение к базе данных.
"""

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """
    Настройки для Album сервиса.
    
    Расширяет настройки базы данных специфичными для Album сервиса параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения
    
    # Database name for Album service
    db_name: str = Field(default="albumdb", description="Имя базы данных для Album сервиса")