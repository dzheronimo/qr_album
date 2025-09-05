"""
Конфигурация для Billing сервиса.

Содержит настройки для Billing сервиса, включая подключение к базе данных.
"""

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """
    Настройки для Billing сервиса.
    
    Расширяет настройки базы данных специфичными для Billing сервиса параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения
    
    # Database name for Billing service
    db_name: str = Field(default="billingdb", description="Имя базы данных для Billing сервиса")