"""
Конфигурация для Print сервиса.

Содержит настройки приложения и переменные окружения.
"""

import os
from typing import List

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """Настройки приложения."""
    
    # Основные настройки
    app_name: str = "Print Service"
    debug: bool = False
    
    # Database name for this service
    db_name: str = Field(default="storyqr_print", description="Имя базы данных для Print сервиса")
    
    # Настройки CORS
    allowed_origins: List[str] = ["*"]
    
    # Настройки WeasyPrint
    weasyprint_enabled: bool = True
    weasyprint_timeout: int = 30  # секунды
    weasyprint_retry_attempts: int = 3
    
    # Настройки очереди печати
    queue_enabled: bool = True
    max_concurrent_jobs: int = 5
    queue_cleanup_interval: int = 3600  # секунды
    
    # Настройки файлов
    output_directory: str = "/tmp/print_output"
    file_retention_days: int = 7
    max_file_size_mb: int = 100
    
    # Настройки качества
    default_quality: int = 300  # DPI
    supported_formats: List[str] = ["pdf", "png", "jpg", "svg"]
    supported_page_sizes: List[str] = ["A4", "A5", "Letter", "Legal"]
    
    # Настройки шаблонов
    max_templates_per_type: int = 100
    template_validation_enabled: bool = True
    
    # Настройки макетов
    max_layouts_per_type: int = 50
    layout_validation_enabled: bool = True


# Создаем экземпляр настроек
settings = Settings()