"""
Роуты для Billing сервиса.

Содержит роуты для работы с подписками, платежами и тарифами.
"""

from .health import router as health_router
from .subscriptions import router as subscriptions_router
from .payments import router as payments_router
from .plans import router as plans_router
from .usage import router as usage_router
from .limits import router as limits_router

__all__ = ["health_router", "subscriptions_router", "payments_router", "plans_router", "usage_router", "limits_router"]
