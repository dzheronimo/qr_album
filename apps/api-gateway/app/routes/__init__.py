"""
Роуты для API Gateway.

Содержит роуты для маршрутизации запросов к микросервисам.
"""

from .health import router as health_router
from .proxy import router as proxy_router
from .auth import router as auth_router

__all__ = ["health_router", "proxy_router", "auth_router"]
