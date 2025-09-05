"""
Общие компоненты для интеграции между сервисами.

Содержит утилиты для RabbitMQ, HTTP клиентов, Redis и обработки ошибок.
"""

from .rabbitmq import RabbitMQClient, EventPublisher, EventConsumer
from .http_client import ServiceHTTPClient, HTTPClientManager
from .redis_client import RedisClient, CacheManager
from .error_handling import IntegrationError, RetryConfig, CircuitBreaker

__all__ = [
    "RabbitMQClient", "EventPublisher", "EventConsumer",
    "ServiceHTTPClient", "HTTPClientManager", 
    "RedisClient", "CacheManager",
    "IntegrationError", "RetryConfig", "CircuitBreaker"
]
