"""
Модели для QR сервиса.

Содержит все SQLAlchemy модели для QR сервиса.
"""

from app.models.short_link import Base, ShortLink

__all__ = ["Base", "ShortLink"]
