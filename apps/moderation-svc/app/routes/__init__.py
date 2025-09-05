"""
Роуты для Moderation сервиса.

Содержит роуты для работы с модерацией контента.
"""

from .health import router as health_router
from .moderation import router as moderation_router
from .rules import router as rules_router
from .logs import router as logs_router
from .ai import router as ai_router

__all__ = ["health_router", "moderation_router", "rules_router", "logs_router", "ai_router"]
