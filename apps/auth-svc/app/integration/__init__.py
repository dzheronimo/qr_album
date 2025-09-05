"""
Интеграция auth-svc с другими сервисами.

Содержит настройки для RabbitMQ, HTTP клиентов и Redis.
"""

from .event_handlers import EventHandlers
from .service_clients import ServiceClients
from .cache_manager import CacheManager

__all__ = ["EventHandlers", "ServiceClients", "CacheManager"]
