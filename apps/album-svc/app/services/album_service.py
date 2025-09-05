"""
Сервис для работы с альбомами.

Содержит бизнес-логику для CRUD операций с альбомами.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError

from app.models.album import Album, AlbumStatus


class AlbumService:
    """Сервис для работы с альбомами."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_album(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        is_public: bool = False,
        tags: Optional[str] = None
    ) -> Album:
        """
        Создание нового альбома.
        
        Args:
            user_id: ID пользователя
            title: Название альбома
            description: Описание альбома
            is_public: Публичный ли альбом
            tags: Теги альбома (JSON строка)
            
        Returns:
            Album: Созданный альбом
        """
        album = Album(
            user_id=user_id,
            title=title,
            description=description,
            is_public=is_public,
            tags=tags,
            status=AlbumStatus.DRAFT
        )
        
        try:
            self.db.add(album)
            await self.db.commit()
            await self.db.refresh(album)
            return album
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании альбома")
    
    async def get_album_by_id(self, album_id: int, user_id: Optional[int] = None) -> Optional[Album]:
        """
        Получение альбома по ID.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя (для проверки доступа)
            
        Returns:
            Optional[Album]: Альбом или None
        """
        query = select(Album).where(Album.id == album_id)
        
        # Если указан user_id, проверяем доступ
        if user_id is not None:
            query = query.where(
                (Album.user_id == user_id) | (Album.is_public == True)
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_albums(
        self,
        user_id: int,
        status: Optional[AlbumStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Album]:
        """
        Получение альбомов пользователя.
        
        Args:
            user_id: ID пользователя
            status: Фильтр по статусу
            limit: Лимит записей
            offset: Смещение
            
        Returns:
            List[Album]: Список альбомов
        """
        query = select(Album).where(Album.user_id == user_id)
        
        if status is not None:
            query = query.where(Album.status == status)
        
        query = query.order_by(Album.updated_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_public_albums(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Album]:
        """
        Получение публичных альбомов.
        
        Args:
            limit: Лимит записей
            offset: Смещение
            
        Returns:
            List[Album]: Список публичных альбомов
        """
        query = (
            select(Album)
            .where(Album.is_public == True)
            .where(Album.status == AlbumStatus.PUBLISHED)
            .order_by(Album.published_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_album(
        self,
        album_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
        tags: Optional[str] = None,
        cover_image_url: Optional[str] = None
    ) -> Optional[Album]:
        """
        Обновление альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            title: Новое название
            description: Новое описание
            is_public: Публичность
            tags: Новые теги
            cover_image_url: URL обложки
            
        Returns:
            Optional[Album]: Обновленный альбом или None
        """
        # Проверяем, что альбом принадлежит пользователю
        album = await self.get_album_by_id(album_id, user_id)
        if not album or album.user_id != user_id:
            return None
        
        update_data = {}
        
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if is_public is not None:
            update_data["is_public"] = is_public
        if tags is not None:
            update_data["tags"] = tags
        if cover_image_url is not None:
            update_data["cover_image_url"] = cover_image_url
        
        if not update_data:
            return album
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(Album)
            .where(Album.id == album_id)
            .where(Album.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_album_by_id(album_id, user_id)
    
    async def publish_album(self, album_id: int, user_id: int) -> bool:
        """
        Публикация альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            
        Returns:
            bool: True если публикация успешна, False иначе
        """
        album = await self.get_album_by_id(album_id, user_id)
        if not album or album.user_id != user_id:
            return False
        
        await self.db.execute(
            update(Album)
            .where(Album.id == album_id)
            .where(Album.user_id == user_id)
            .values(
                status=AlbumStatus.PUBLISHED,
                published_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def archive_album(self, album_id: int, user_id: int) -> bool:
        """
        Архивирование альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            
        Returns:
            bool: True если архивирование успешно, False иначе
        """
        album = await self.get_album_by_id(album_id, user_id)
        if not album or album.user_id != user_id:
            return False
        
        await self.db.execute(
            update(Album)
            .where(Album.id == album_id)
            .where(Album.user_id == user_id)
            .values(
                status=AlbumStatus.ARCHIVED,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def delete_album(self, album_id: int, user_id: int) -> bool:
        """
        Удаление альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        album = await self.get_album_by_id(album_id, user_id)
        if not album or album.user_id != user_id:
            return False
        
        await self.db.execute(
            delete(Album)
            .where(Album.id == album_id)
            .where(Album.user_id == user_id)
        )
        await self.db.commit()
        
        return True
    
    async def get_album_stats(self, album_id: int, user_id: int) -> Optional[dict]:
        """
        Получение статистики альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            
        Returns:
            Optional[dict]: Статистика альбома или None
        """
        album = await self.get_album_by_id(album_id, user_id)
        if not album or album.user_id != user_id:
            return None
        
        # Подсчет страниц
        pages_count = len(album.pages) if album.pages else 0
        
        return {
            "album_id": album_id,
            "pages_count": pages_count,
            "status": album.status.value,
            "is_public": album.is_public,
            "created_at": album.created_at.isoformat() if album.created_at else None,
            "updated_at": album.updated_at.isoformat() if album.updated_at else None,
            "published_at": album.published_at.isoformat() if album.published_at else None,
        }
