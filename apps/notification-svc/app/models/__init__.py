"""
Модели для Notification сервиса.

Содержит SQLAlchemy модели для работы с уведомлениями и шаблонами.
"""

from .notification import Notification, NotificationTemplate, NotificationSettings, NotificationQueue

__all__ = ["Notification", "NotificationTemplate", "NotificationSettings", "NotificationQueue"]
