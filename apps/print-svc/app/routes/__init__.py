"""
Роуты для Print сервиса.

Содержит роуты для работы с печатью и PDF генерацией.
"""

from .health import router as health_router
from .print import router as print_router
from .templates import router as templates_router
from .layouts import router as layouts_router
from .queue import router as queue_router

__all__ = ["health_router", "print_router", "templates_router", "layouts_router", "queue_router"]
