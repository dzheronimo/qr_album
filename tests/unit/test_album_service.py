"""
Unit тесты для album-svc.

Тестирует бизнес-логику сервиса альбомов.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from apps.album_svc.app.services.album_service import AlbumService
from apps.album_svc.app.models.album import Album, Page
from apps.album_svc.app.schemas.album import AlbumCreate, AlbumUpdate, PageCreate, PageUpdate


class TestAlbumService:
    """Тесты для AlbumService."""
    
    @pytest_asyncio.fixture
    async def album_service(self, test_db_session: AsyncSession):
        """Фикстура для AlbumService."""
        return AlbumService(test_db_session)
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_create_album_success(self, album_service: AlbumService, test_album_data: dict):
        """Тест успешного создания альбома."""
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        assert album.title == test_album_data["title"]
        assert album.description == test_album_data["description"]
        assert album.user_id == test_album_data["user_id"]
        assert album.is_public == test_album_data["is_public"]
        assert album.is_active is True
        assert album.created_at is not None
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_get_album_by_id(self, album_service: AlbumService, test_album_data: dict):
        """Тест получения альбома по ID."""
        # Создаем альбом
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        created_album = await album_service.create_album(album_data)
        
        # Получаем альбом по ID
        found_album = await album_service.get_album_by_id(created_album.id)
        
        assert found_album.id == created_album.id
        assert found_album.title == created_album.title
        assert found_album.user_id == created_album.user_id
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_get_user_albums(self, album_service: AlbumService, test_album_data: dict):
        """Тест получения альбомов пользователя."""
        user_id = test_album_data["user_id"]
        
        # Создаем несколько альбомов
        for i in range(3):
            album_data = AlbumCreate(
                title=f"Album {i}",
                description=f"Description {i}",
                user_id=user_id,
                is_public=True
            )
            await album_service.create_album(album_data)
        
        # Получаем альбомы пользователя
        albums = await album_service.get_user_albums(user_id)
        
        assert len(albums) == 3
        for album in albums:
            assert album.user_id == user_id
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_update_album_success(self, album_service: AlbumService, test_album_data: dict):
        """Тест успешного обновления альбома."""
        # Создаем альбом
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        created_album = await album_service.create_album(album_data)
        
        # Обновляем альбом
        update_data = AlbumUpdate(
            title="Updated Title",
            description="Updated Description"
        )
        
        updated_album = await album_service.update_album(created_album.id, update_data)
        
        assert updated_album.title == "Updated Title"
        assert updated_album.description == "Updated Description"
        assert updated_album.user_id == created_album.user_id  # Не изменился
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_delete_album(self, album_service: AlbumService, test_album_data: dict):
        """Тест удаления альбома."""
        # Создаем альбом
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        created_album = await album_service.create_album(album_data)
        
        # Удаляем альбом
        success = await album_service.delete_album(created_album.id)
        assert success is True
        
        # Проверяем, что альбом не найден
        found_album = await album_service.get_album_by_id(created_album.id)
        assert found_album is None
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_create_page_success(self, album_service: AlbumService, test_album_data: dict, test_page_data: dict):
        """Тест успешного создания страницы."""
        # Создаем альбом
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        # Создаем страницу
        page_data = PageCreate(
            title=test_page_data["title"],
            content=test_page_data["content"],
            album_id=album.id,
            page_number=test_page_data["page_number"]
        )
        
        page = await album_service.create_page(page_data)
        
        assert page.title == test_page_data["title"]
        assert page.content == test_page_data["content"]
        assert page.album_id == album.id
        assert page.page_number == test_page_data["page_number"]
        assert page.is_active is True
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_get_page_by_id(self, album_service: AlbumService, test_album_data: dict, test_page_data: dict):
        """Тест получения страницы по ID."""
        # Создаем альбом и страницу
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        page_data = PageCreate(
            title=test_page_data["title"],
            content=test_page_data["content"],
            album_id=album.id,
            page_number=test_page_data["page_number"]
        )
        
        created_page = await album_service.create_page(page_data)
        
        # Получаем страницу по ID
        found_page = await album_service.get_page_by_id(created_page.id)
        
        assert found_page.id == created_page.id
        assert found_page.title == created_page.title
        assert found_page.album_id == created_page.album_id
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_get_album_pages(self, album_service: AlbumService, test_album_data: dict, test_page_data: dict):
        """Тест получения страниц альбома."""
        # Создаем альбом
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        # Создаем несколько страниц
        for i in range(3):
            page_data = PageCreate(
                title=f"Page {i}",
                content=f"Content {i}",
                album_id=album.id,
                page_number=i + 1
            )
            await album_service.create_page(page_data)
        
        # Получаем страницы альбома
        pages = await album_service.get_album_pages(album.id)
        
        assert len(pages) == 3
        for page in pages:
            assert page.album_id == album.id
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_update_page_success(self, album_service: AlbumService, test_album_data: dict, test_page_data: dict):
        """Тест успешного обновления страницы."""
        # Создаем альбом и страницу
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        page_data = PageCreate(
            title=test_page_data["title"],
            content=test_page_data["content"],
            album_id=album.id,
            page_number=test_page_data["page_number"]
        )
        
        created_page = await album_service.create_page(page_data)
        
        # Обновляем страницу
        update_data = PageUpdate(
            title="Updated Page Title",
            content="Updated Page Content"
        )
        
        updated_page = await album_service.update_page(created_page.id, update_data)
        
        assert updated_page.title == "Updated Page Title"
        assert updated_page.content == "Updated Page Content"
        assert updated_page.album_id == created_page.album_id  # Не изменился
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_delete_page(self, album_service: AlbumService, test_album_data: dict, test_page_data: dict):
        """Тест удаления страницы."""
        # Создаем альбом и страницу
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=test_album_data["user_id"],
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        page_data = PageCreate(
            title=test_page_data["title"],
            content=test_page_data["content"],
            album_id=album.id,
            page_number=test_page_data["page_number"]
        )
        
        created_page = await album_service.create_page(page_data)
        
        # Удаляем страницу
        success = await album_service.delete_page(created_page.id)
        assert success is True
        
        # Проверяем, что страница не найдена
        found_page = await album_service.get_page_by_id(created_page.id)
        assert found_page is None
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_get_public_albums(self, album_service: AlbumService, test_album_data: dict):
        """Тест получения публичных альбомов."""
        user_id = test_album_data["user_id"]
        
        # Создаем публичные и приватные альбомы
        for i in range(3):
            album_data = AlbumCreate(
                title=f"Public Album {i}",
                description=f"Public Description {i}",
                user_id=user_id,
                is_public=True
            )
            await album_service.create_album(album_data)
        
        for i in range(2):
            album_data = AlbumCreate(
                title=f"Private Album {i}",
                description=f"Private Description {i}",
                user_id=user_id,
                is_public=False
            )
            await album_service.create_album(album_data)
        
        # Получаем только публичные альбомы
        public_albums = await album_service.get_public_albums()
        
        assert len(public_albums) == 3
        for album in public_albums:
            assert album.is_public is True
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_search_albums(self, album_service: AlbumService, test_album_data: dict):
        """Тест поиска альбомов."""
        user_id = test_album_data["user_id"]
        
        # Создаем альбомы с разными названиями
        album_titles = ["Python Programming", "Java Development", "Web Design", "Mobile Apps"]
        
        for title in album_titles:
            album_data = AlbumCreate(
                title=title,
                description=f"Description for {title}",
                user_id=user_id,
                is_public=True
            )
            await album_service.create_album(album_data)
        
        # Ищем альбомы по ключевому слову
        search_results = await album_service.search_albums("Python")
        
        assert len(search_results) == 1
        assert search_results[0].title == "Python Programming"
        
        # Ищем альбомы по другому ключевому слову
        search_results = await album_service.search_albums("Development")
        
        assert len(search_results) == 1
        assert search_results[0].title == "Java Development"
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_album_ownership_check(self, album_service: AlbumService, test_album_data: dict):
        """Тест проверки владения альбомом."""
        user_id = test_album_data["user_id"]
        other_user_id = 999
        
        # Создаем альбом
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=user_id,
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        # Проверяем владение владельцем
        is_owner = await album_service.is_album_owner(album.id, user_id)
        assert is_owner is True
        
        # Проверяем владение другим пользователем
        is_owner = await album_service.is_album_owner(album.id, other_user_id)
        assert is_owner is False
    
    @pytest.mark.unit
    @pytest.mark.album
    async def test_album_stats(self, album_service: AlbumService, test_album_data: dict, test_page_data: dict):
        """Тест статистики альбома."""
        user_id = test_album_data["user_id"]
        
        # Создаем альбом
        album_data = AlbumCreate(
            title=test_album_data["title"],
            description=test_album_data["description"],
            user_id=user_id,
            is_public=test_album_data["is_public"]
        )
        
        album = await album_service.create_album(album_data)
        
        # Создаем несколько страниц
        for i in range(5):
            page_data = PageCreate(
                title=f"Page {i}",
                content=f"Content {i}",
                album_id=album.id,
                page_number=i + 1
            )
            await album_service.create_page(page_data)
        
        # Получаем статистику альбома
        stats = await album_service.get_album_stats(album.id)
        
        assert stats["total_pages"] == 5
        assert stats["album_id"] == album.id
        assert "created_at" in stats
