"""
Конфигурация для Moderation сервиса.

Содержит настройки приложения и переменные окружения.
"""

import os
from typing import List

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """Настройки приложения."""
    
    # Основные настройки
    app_name: str = "Moderation Service"
    debug: bool = False
    
    # Database name for this service
    db_name: str = Field(default="storyqr_moderation", description="Имя базы данных для Moderation сервиса")
    
    # Настройки CORS
    allowed_origins: List[str] = ["*"]
    
    # Настройки AI модерации
    ai_enabled: bool = True
    ai_models: dict = {
        "text": "text-moderation-v1",
        "image": "image-moderation-v1",
        "video": "video-moderation-v1"
    }
    ai_timeout: int = 30  # секунды
    ai_retry_attempts: int = 3
    
    # Настройки автоматической модерации
    auto_moderation_enabled: bool = True
    auto_approve_threshold: float = 0.9
    auto_reject_threshold: float = 0.1
    
    # Настройки уведомлений
    notify_on_flag: bool = True
    notify_on_reject: bool = True
    
    # Настройки журнала
    log_retention_days: int = 90
    log_cleanup_interval_hours: int = 24
    
    # Настройки правил
    max_rules_per_content_type: int = 100
    rule_evaluation_timeout: int = 5  # секунды


# Создаем экземпляр настроек
settings = Settings()