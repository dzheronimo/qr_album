"""
Сервис для работы со страницами альбомов.

Содержит бизнес-логику для CRUD операций со страницами.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError

from app.models.album import Page, PageStatus, Album


class PageService:
    """Сервис для работы со страницами альбомов."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_page(
        self,
        album_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        order_index: Optional[int] = None
    ) -> Optional[Page]:
        """
        Создание новой страницы.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            title: Заголовок страницы
            content: Содержимое страницы
            order_index: Порядковый номер страницы
            
        Returns:
            Optional[Page]: Созданная страница или None
        """
        # Проверяем, что альбом принадлежит пользователю
        album_query = select(Album).where(Album.id == album_id, Album.user_id == user_id)
        album_result = await self.db.execute(album_query)
        album = album_result.scalar_one_or_none()
        
        if not album:
            return None
        
        # Если order_index не указан, ставим в конец
        if order_index is None:
            max_order_query = select(func.max(Page.order_index)).where(Page.album_id == album_id)
            max_order_result = await self.db.execute(max_order_query)
            max_order = max_order_result.scalar() or 0
            order_index = max_order + 1
        
        page = Page(
            album_id=album_id,
            title=title,
            content=content,
            order_index=order_index,
            status=PageStatus.DRAFT
        )
        
        try:
            self.db.add(page)
            await self.db.commit()
            await self.db.refresh(page)
            return page
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании страницы")
    
    async def get_page_by_id(self, page_id: int, user_id: Optional[int] = None) -> Optional[Page]:
        """
        Получение страницы по ID.
        
        Args:
            page_id: ID страницы
            user_id: ID пользователя (для проверки доступа)
            
        Returns:
            Optional[Page]: Страница или None
        """
        query = select(Page).where(Page.id == page_id)
        
        # Если указан user_id, проверяем доступ через альбом
        if user_id is not None:
            query = query.join(Album).where(
                (Album.user_id == user_id) | (Album.is_public == True)
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_album_pages(
        self,
        album_id: int,
        user_id: Optional[int] = None,
        status: Optional[PageStatus] = None
    ) -> List[Page]:
        """
        Получение страниц альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя (для проверки доступа)
            status: Фильтр по статусу
            
        Returns:
            List[Page]: Список страниц
        """
        query = select(Page).where(Page.album_id == album_id)
        
        # Если указан user_id, проверяем доступ через альбом
        if user_id is not None:
            query = query.join(Album).where(
                (Album.user_id == user_id) | (Album.is_public == True)
            )
        
        if status is not None:
            query = query.where(Page.status == status)
        
        query = query.order_by(Page.order_index.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_page(
        self,
        page_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        order_index: Optional[int] = None,
        background_color: Optional[str] = None,
        text_color: Optional[str] = None,
        font_family: Optional[str] = None,
        font_size: Optional[int] = None
    ) -> Optional[Page]:
        """
        Обновление страницы.
        
        Args:
            page_id: ID страницы
            user_id: ID пользователя
            title: Новый заголовок
            content: Новое содержимое
            order_index: Новый порядковый номер
            background_color: Цвет фона
            text_color: Цвет текста
            font_family: Шрифт
            font_size: Размер шрифта
            
        Returns:
            Optional[Page]: Обновленная страница или None
        """
        # Проверяем доступ к странице
        page = await self.get_page_by_id(page_id, user_id)
        if not page:
            return None
        
        # Проверяем, что альбом принадлежит пользователю
        album_query = select(Album).where(Album.id == page.album_id, Album.user_id == user_id)
        album_result = await self.db.execute(album_query)
        album = album_result.scalar_one_or_none()
        
        if not album:
            return None
        
        update_data = {}
        
        if title is not None:
            update_data["title"] = title
        if content is not None:
            update_data["content"] = content
        if order_index is not None:
            update_data["order_index"] = order_index
        if background_color is not None:
            update_data["background_color"] = background_color
        if text_color is not None:
            update_data["text_color"] = text_color
        if font_family is not None:
            update_data["font_family"] = font_family
        if font_size is not None:
            update_data["font_size"] = font_size
        
        if not update_data:
            return page
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(Page)
            .where(Page.id == page_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_page_by_id(page_id, user_id)
    
    async def publish_page(self, page_id: int, user_id: int) -> bool:
        """
        Публикация страницы.
        
        Args:
            page_id: ID страницы
            user_id: ID пользователя
            
        Returns:
            bool: True если публикация успешна, False иначе
        """
        page = await self.get_page_by_id(page_id, user_id)
        if not page:
            return False
        
        # Проверяем, что альбом принадлежит пользователю
        album_query = select(Album).where(Album.id == page.album_id, Album.user_id == user_id)
        album_result = await self.db.execute(album_query)
        album = album_result.scalar_one_or_none()
        
        if not album:
            return False
        
        await self.db.execute(
            update(Page)
            .where(Page.id == page_id)
            .values(
                status=PageStatus.PUBLISHED,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def archive_page(self, page_id: int, user_id: int) -> bool:
        """
        Архивирование страницы.
        
        Args:
            page_id: ID страницы
            user_id: ID пользователя
            
        Returns:
            bool: True если архивирование успешно, False иначе
        """
        page = await self.get_page_by_id(page_id, user_id)
        if not page:
            return False
        
        # Проверяем, что альбом принадлежит пользователю
        album_query = select(Album).where(Album.id == page.album_id, Album.user_id == user_id)
        album_result = await self.db.execute(album_query)
        album = album_result.scalar_one_or_none()
        
        if not album:
            return False
        
        await self.db.execute(
            update(Page)
            .where(Page.id == page_id)
            .values(
                status=PageStatus.ARCHIVED,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def delete_page(self, page_id: int, user_id: int) -> bool:
        """
        Удаление страницы.
        
        Args:
            page_id: ID страницы
            user_id: ID пользователя
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        page = await self.get_page_by_id(page_id, user_id)
        if not page:
            return False
        
        # Проверяем, что альбом принадлежит пользователю
        album_query = select(Album).where(Album.id == page.album_id, Album.user_id == user_id)
        album_result = await self.db.execute(album_query)
        album = album_result.scalar_one_or_none()
        
        if not album:
            return False
        
        await self.db.execute(
            delete(Page)
            .where(Page.id == page_id)
        )
        await self.db.commit()
        
        return True
    
    async def reorder_pages(self, album_id: int, user_id: int, page_orders: List[dict]) -> bool:
        """
        Изменение порядка страниц в альбоме.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя
            page_orders: Список с ID страниц и их новыми порядковыми номерами
            
        Returns:
            bool: True если изменение порядка успешно, False иначе
        """
        # Проверяем, что альбом принадлежит пользователю
        album_query = select(Album).where(Album.id == album_id, Album.user_id == user_id)
        album_result = await self.db.execute(album_query)
        album = album_result.scalar_one_or_none()
        
        if not album:
            return False
        
        # Обновляем порядок страниц
        for page_order in page_orders:
            page_id = page_order.get("page_id")
            order_index = page_order.get("order_index")
            
            if page_id is not None and order_index is not None:
                await self.db.execute(
                    update(Page)
                    .where(Page.id == page_id)
                    .where(Page.album_id == album_id)
                    .values(
                        order_index=order_index,
                        updated_at=datetime.utcnow()
                    )
                )
        
        await self.db.commit()
        return True
