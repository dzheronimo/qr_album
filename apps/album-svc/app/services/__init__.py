"""
Сервисы для Album сервиса.

Содержит бизнес-логику для работы с альбомами и страницами.
"""

from .album_service import AlbumService
from .page_service import PageService

__all__ = ["AlbumService", "PageService"]
