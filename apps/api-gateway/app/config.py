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
    admin_origins: str = "http://localhost:3001,http://127.0.0.1:3001,https://admin.yourdomain.com"
    web_origins: str = "http://localhost:3000,http://127.0.0.1:3000,https://yourdomain.com"
    cors_allow_credentials: bool = True
    
    @property
    def cors_origins(self) -> list:
        """Получает список разрешенных CORS origins."""
        admin_origins = self.admin_origins.split(',') if self.admin_origins else []
        web_origins = self.web_origins.split(',') if self.web_origins else []
        origins = admin_origins + web_origins
        
        # Если origins не заданы, используем безопасные по умолчанию
        if not origins:
            origins = [
                "http://localhost:3000", 
                "http://localhost:3001",
                "http://127.0.0.1:3000", 
                "http://127.0.0.1:3001"
            ]
        
        return origins
    
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