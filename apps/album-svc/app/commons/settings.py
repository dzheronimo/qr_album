"""
Общие настройки для всех микросервисов.

Содержит базовые классы настроек с общими переменными окружения
для всех сервисов в системе.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """
    Базовые настройки, общие для всех микросервисов.
    
    Содержит общие переменные окружения, такие как JWT секрет,
    базовый URL, настройки Redis и RabbitMQ.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # JWT Configuration
    jwt_secret: str = Field(..., description="Секретный ключ для JWT токенов")
    jwt_algorithm: str = Field(default="HS256", description="Алгоритм подписи JWT")
    jwt_access_token_expire_minutes: int = Field(
        default=15, 
        description="Время жизни access токена в минутах"
    )

    # Public Configuration
    public_base_url: str = Field(
        default="http://localhost:8080",
        description="Базовый публичный URL системы"
    )

    # Redis Configuration
    redis_host: str = Field(default="redis", description="Хост Redis сервера")
    redis_port: int = Field(default=6379, description="Порт Redis сервера")
    redis_password: Optional[str] = Field(default=None, description="Пароль Redis")
    redis_db: int = Field(default=0, description="Номер базы данных Redis")

    @property
    def redis_url(self) -> str:
        """
        Формирует URL для подключения к Redis.
        
        Returns:
            URL для подключения к Redis
        """
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # RabbitMQ Configuration
    rabbitmq_host: str = Field(default="rabbit", description="Хост RabbitMQ сервера")
    rabbitmq_port: int = Field(default=5672, description="Порт RabbitMQ сервера")
    rabbitmq_user: str = Field(default="guest", description="Пользователь RabbitMQ")
    rabbitmq_password: str = Field(default="guest", description="Пароль RabbitMQ")
    rabbitmq_vhost: str = Field(default="/", description="Виртуальный хост RabbitMQ")

    @property
    def rabbitmq_url(self) -> str:
        """
        Формирует URL для подключения к RabbitMQ.
        
        Returns:
            URL для подключения к RabbitMQ
        """
        return (
            f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_vhost}"
        )

    # PostgreSQL Configuration
    postgres_host: str = Field(default="postgres", description="Хост PostgreSQL сервера")
    postgres_port: int = Field(default=5432, description="Порт PostgreSQL сервера")
    postgres_user: str = Field(default="postgres", description="Пользователь PostgreSQL")
    postgres_password: str = Field(default="postgres", description="Пароль PostgreSQL")

    # MinIO Configuration
    minio_endpoint: str = Field(default="minio:9000", description="Endpoint MinIO")
    minio_access_key: str = Field(default="minioadmin", description="Access key MinIO")
    minio_secret_key: str = Field(default="minioadmin", description="Secret key MinIO")
    minio_bucket_name: str = Field(
        default="qr-albums-media", 
        description="Имя bucket для медиафайлов"
    )
    minio_secure: bool = Field(default=False, description="Использовать HTTPS для MinIO")

    # SMTP Configuration
    smtp_host: str = Field(default="mailhog", description="SMTP хост")
    smtp_port: int = Field(default=1025, description="SMTP порт")
    smtp_user: Optional[str] = Field(default=None, description="SMTP пользователь")
    smtp_password: Optional[str] = Field(default=None, description="SMTP пароль")
    smtp_use_tls: bool = Field(default=False, description="Использовать TLS для SMTP")
    smtp_from_email: str = Field(
        default="noreply@qr-albums.com",
        description="Email отправителя по умолчанию"
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        description="Лимит запросов в минуту на IP"
    )

    # Service URLs
    api_gateway_url: str = Field(
        default="http://api-gateway:8000",
        description="URL API Gateway"
    )
    auth_svc_url: str = Field(default="http://auth-svc:8000", description="URL Auth Service")
    user_profile_svc_url: str = Field(
        default="http://user-profile-svc:8000",
        description="URL User Profile Service"
    )
    album_svc_url: str = Field(default="http://album-svc:8000", description="URL Album Service")
    media_svc_url: str = Field(default="http://media-svc:8000", description="URL Media Service")
    qr_svc_url: str = Field(default="http://qr-svc:8000", description="URL QR Service")
    scan_gateway_url: str = Field(
        default="http://scan-gateway:8000",
        description="URL Scan Gateway"
    )
    print_svc_url: str = Field(default="http://print-svc:8000", description="URL Print Service")
    analytics_svc_url: str = Field(
        default="http://analytics-svc:8000",
        description="URL Analytics Service"
    )
    billing_svc_url: str = Field(
        default="http://billing-svc:8000",
        description="URL Billing Service"
    )
    notification_svc_url: str = Field(
        default="http://notification-svc:8000",
        description="URL Notification Service"
    )
    moderation_svc_url: str = Field(
        default="http://moderation-svc:8000",
        description="URL Moderation Service"
    )


class DatabaseSettings(CommonSettings):
    """
    Настройки для сервисов с базой данных.
    
    Расширяет CommonSettings добавлением настроек базы данных.
    """
    
    # Database name - должно быть переопределено в каждом сервисе
    db_name: str = Field(..., description="Имя базы данных для сервиса")

    @property
    def database_url(self) -> str:
        """
        Формирует URL для подключения к базе данных.
        
        Returns:
            URL для подключения к PostgreSQL
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.db_name}"
        )