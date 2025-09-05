"""
Конфигурация для QR сервиса.

Содержит настройки для QR сервиса, включая подключение к базе данных,
Redis и другие параметры.
"""

from pydantic import Field
from app.commons.settings import DatabaseSettings


class Settings(DatabaseSettings):
    """
    Настройки для QR сервиса.
    
    Расширяет настройки базы данных специфичными для QR сервиса параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения
    
    # Database name for QR service
    db_name: str = Field(default="qrdb", description="Имя базы данных для QR сервиса")
    
    # Scan Gateway URL
    scan_gateway_url: str = Field(default="http://localhost:8004", description="URL сервиса scan-gateway")
    
    # QR Service specific settings
    hashids_salt: str = Field(
        default="qr-albums-salt-change-in-production",
        description="Соль для Hashids"
    )
    hashids_min_length: int = Field(
        default=5,
        description="Минимальная длина slug"
    )