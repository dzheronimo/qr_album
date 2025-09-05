"""
Конфигурация для Media сервиса.

Содержит настройки для Media сервиса, включая подключение к MinIO,
базе данных и другие параметры.
"""

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """
    Настройки для Media сервиса.
    
    Расширяет настройки базы данных специфичными для Media сервиса параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения
    
    # Database name for Media service
    db_name: str = Field(default="mediadb", description="Имя базы данных для Media сервиса")