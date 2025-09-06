"""
Конфигурация для Notification сервиса.

Содержит настройки приложения и переменные окружения.
"""

import os
from typing import List

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """Настройки приложения."""
    
    # Основные настройки
    app_name: str = "Notification Service"
    debug: bool = False
    
    # Database name for this service
    db_name: str = Field(default="storyqr_notification", description="Имя базы данных для Notification сервиса")
    
    # Настройки CORS
    allowed_origins: List[str] = ["*"]
    
    # Настройки уведомлений
    max_notification_attempts: int = 3
    notification_retry_delay: int = 300  # секунды
    
    # Настройки очереди
    queue_batch_size: int = 10
    queue_cleanup_days: int = 7
    
    # Настройки email (для будущей интеграции)
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    
    # Настройки push уведомлений (для будущей интеграции)
    firebase_server_key: str = ""
    
    # Настройки SMS (для будущей интеграции)
    sms_provider: str = ""
    sms_api_key: str = ""


# Создаем экземпляр настроек
settings = Settings()