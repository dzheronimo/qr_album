"""
Роуты для Notification сервиса.

Содержит роуты для работы с уведомлениями, шаблонами и настройками.
"""

from .health import router as health_router
from .notifications import router as notifications_router
from .templates import router as templates_router
from .settings import router as settings_router
from .queue import router as queue_router

__all__ = ["health_router", "notifications_router", "templates_router", "settings_router", "queue_router"]
