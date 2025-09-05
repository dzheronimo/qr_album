"""
Модели для User Profile сервиса.

Содержит SQLAlchemy модели для работы с профилями пользователей.
"""

from .user_profile import UserProfile, UserSettings

__all__ = ["UserProfile", "UserSettings"]
