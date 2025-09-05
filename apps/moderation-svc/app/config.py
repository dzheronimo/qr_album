"""
Конфигурация для Moderation сервиса.

Содержит настройки приложения и переменные окружения.
"""

import os
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # Основные настройки
    app_name: str = "Moderation Service"
    debug: bool = False
    
    # Настройки базы данных
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/moderation_db"
    
    # Настройки CORS
    allowed_origins: List[str] = ["*"]
    
    # Настройки JWT (для будущей интеграции)
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
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
    
    class Config:
        """Конфигурация Pydantic."""
        env_file = ".env"
        case_sensitive = False