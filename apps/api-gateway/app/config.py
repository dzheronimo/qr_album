"""
Конфигурация для API Gateway сервиса.

Содержит настройки для API Gateway, включая JWT секрет,
базовый URL и другие параметры.
"""

from app.commons.settings import CommonSettings


class Settings(CommonSettings):
    """Настройки для API Gateway."""
    
    # URL микросервисов
    auth_service_url: str = "http://auth-svc:8000"
    user_profile_service_url: str = "http://user-profile-svc:8000"
    album_service_url: str = "http://album-svc:8000"
    media_service_url: str = "http://media-svc:8000"
    qr_service_url: str = "http://qr-svc:8000"
    analytics_service_url: str = "http://analytics-svc:8000"
    billing_service_url: str = "http://billing-svc:8000"
    notification_service_url: str = "http://notification-svc:8000"
    moderation_service_url: str = "http://moderation-svc:8000"
    print_service_url: str = "http://print-svc:8000"
    
    # Настройки CORS
    cors_origins: list = ["*"]  # В продакшене указать конкретные домены
    cors_allow_credentials: bool = True
    
    # Настройки rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    
    # Настройки логирования
    log_level: str = "INFO"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    """
    Настройки для API Gateway сервиса.
    
    Расширяет базовые настройки специфичными для API Gateway параметрами.
    """
    
    model_config = {"env_prefix": ""}  # Без префикса для переменных окружения