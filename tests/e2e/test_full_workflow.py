"""
End-to-End тесты для полного рабочего процесса.

Тестирует полный цикл работы с QR альбомами от создания до сканирования.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from apps.api_gateway.app.main import app as gateway_app
from apps.auth_svc.app.main import app as auth_app
from apps.album_svc.app.main import app as album_app
from apps.media_svc.app.main import app as media_app
from apps.qr_svc.app.main import app as qr_app


class TestFullWorkflow:
    """E2E тесты для полного рабочего процесса."""
    
    @pytest_asyncio.fixture
    async def gateway_client(self):
        """Фикстура для API Gateway клиента."""
        with TestClient(gateway_app) as client:
            yield client
    
    @pytest_asyncio.fixture
    async def auth_client(self):
        """Фикстура для Auth сервиса клиента."""
        with TestClient(auth_app) as client:
            yield client
    
    @pytest_asyncio.fixture
    async def album_client(self):
        """Фикстура для Album сервиса клиента."""
        with TestClient(album_app) as client:
            yield client
    
    @pytest_asyncio.fixture
    async def media_client(self):
        """Фикстура для Media сервиса клиента."""
        with TestClient(media_app) as client:
            yield client
    
    @pytest_asyncio.fixture
    async def qr_client(self):
        """Фикстура для QR сервиса клиента."""
        with TestClient(qr_app) as client:
            yield client
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_complete_album_creation_workflow(
        self, 
        gateway_client: TestClient,
        auth_client: TestClient,
        album_client: TestClient,
        media_client: TestClient,
        qr_client: TestClient
    ):
        """Тест полного процесса создания альбома с QR кодами."""
        
        # 1. Регистрация пользователя
        user_data = {
            "email": "e2e@example.com",
            "username": "e2euser",
            "password": "password123",
            "first_name": "E2E",
            "last_name": "User"
        }
        
        response = auth_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["id"]
        
        # 2. Вход пользователя
        login_data = {
            "email": "e2e@example.com",
            "password": "password123"
        }
        
        response = auth_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 3. Создание альбома
        album_data = {
            "title": "E2E Test Album",
            "description": "Album created during E2E testing",
            "is_public": True
        }
        
        response = album_client.post("/api/v1/albums", json=album_data, headers=headers)
        assert response.status_code == 201
        album_id = response.json()["id"]
        
        # 4. Создание страниц альбома
        pages_data = [
            {
                "title": "Page 1",
                "content": "Content of page 1",
                "page_number": 1
            },
            {
                "title": "Page 2", 
                "content": "Content of page 2",
                "page_number": 2
            },
            {
                "title": "Page 3",
                "content": "Content of page 3", 
                "page_number": 3
            }
        ]
        
        page_ids = []
        for page_data in pages_data:
            response = album_client.post(
                f"/api/v1/albums/{album_id}/pages", 
                json=page_data, 
                headers=headers
            )
            assert response.status_code == 201
            page_ids.append(response.json()["id"])
        
        # 5. Загрузка медиафайлов для страниц
        # Симулируем загрузку файлов
        with patch('apps.media_svc.app.services.media_service.MediaService.upload_file') as mock_upload:
            mock_upload.return_value = {
                "id": 1,
                "filename": "test-image.jpg",
                "file_path": "/uploads/test-image.jpg",
                "file_size": 1024000,
                "mime_type": "image/jpeg"
            }
            
            for i, page_id in enumerate(page_ids):
                # Симулируем загрузку файла
                file_data = {
                    "filename": f"image-{i+1}.jpg",
                    "file_size": 1024000,
                    "mime_type": "image/jpeg"
                }
                
                response = media_client.post(
                    f"/api/v1/media/upload",
                    json=file_data,
                    headers=headers
                )
                assert response.status_code == 201
                media_id = response.json()["id"]
                
                # Привязываем медиафайл к странице
                response = media_client.post(
                    f"/api/v1/media/{media_id}/attach",
                    json={"page_id": page_id},
                    headers=headers
                )
                assert response.status_code == 200
        
        # 6. Генерация QR кодов для страниц
        qr_codes = []
        for page_id in page_ids:
            qr_data = {
                "page_id": page_id,
                "album_id": album_id,
                "custom_url": f"https://example.com/page/{page_id}"
            }
            
            response = qr_client.post(
                "/api/v1/qr/generate",
                json=qr_data,
                headers=headers
            )
            assert response.status_code == 201
            qr_code = response.json()
            qr_codes.append(qr_code)
        
        # 7. Проверка, что все QR коды созданы
        assert len(qr_codes) == 3
        for qr_code in qr_codes:
            assert "id" in qr_code
            assert "url" in qr_code
            assert "qr_code_url" in qr_code
        
        # 8. Получение альбома с полной информацией
        response = album_client.get(f"/api/v1/albums/{album_id}", headers=headers)
        assert response.status_code == 200
        album = response.json()
        
        assert album["id"] == album_id
        assert album["title"] == "E2E Test Album"
        assert len(album["pages"]) == 3
        
        # 9. Проверка, что у каждой страницы есть QR код
        for page in album["pages"]:
            assert "qr_code" in page
            assert page["qr_code"] is not None
        
        # 10. Симуляция сканирования QR кода
        first_qr_code = qr_codes[0]
        
        # Получаем информацию о QR коде
        response = qr_client.get(f"/api/v1/qr/{first_qr_code['id']}", headers=headers)
        assert response.status_code == 200
        qr_info = response.json()
        
        # Симулируем сканирование
        response = qr_client.post(
            f"/api/v1/qr/{first_qr_code['id']}/scan",
            json={"scanner_info": {"ip": "127.0.0.1", "user_agent": "test"}},
            headers=headers
        )
        assert response.status_code == 200
        
        # 11. Проверка статистики сканирований
        response = qr_client.get(f"/api/v1/qr/{first_qr_code['id']}/stats", headers=headers)
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["scan_count"] >= 1
        assert "last_scanned_at" in stats
        
        # 12. Получение аналитики альбома
        response = album_client.get(f"/api/v1/albums/{album_id}/analytics", headers=headers)
        assert response.status_code == 200
        analytics = response.json()
        
        assert "total_pages" in analytics
        assert "total_scans" in analytics
        assert analytics["total_pages"] == 3
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_public_album_access_workflow(
        self,
        gateway_client: TestClient,
        auth_client: TestClient,
        album_client: TestClient,
        qr_client: TestClient
    ):
        """Тест доступа к публичному альбому без авторизации."""
        
        # 1. Создаем пользователя и альбом (как в предыдущем тесте)
        user_data = {
            "email": "public@example.com",
            "username": "publicuser",
            "password": "password123",
            "first_name": "Public",
            "last_name": "User"
        }
        
        response = auth_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        login_data = {
            "email": "public@example.com",
            "password": "password123"
        }
        
        response = auth_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 2. Создаем публичный альбом
        album_data = {
            "title": "Public Test Album",
            "description": "Public album for E2E testing",
            "is_public": True
        }
        
        response = album_client.post("/api/v1/albums", json=album_data, headers=headers)
        assert response.status_code == 201
        album_id = response.json()["id"]
        
        # 3. Создаем страницу
        page_data = {
            "title": "Public Page",
            "content": "Content of public page",
            "page_number": 1
        }
        
        response = album_client.post(
            f"/api/v1/albums/{album_id}/pages",
            json=page_data,
            headers=headers
        )
        assert response.status_code == 201
        page_id = response.json()["id"]
        
        # 4. Генерируем QR код
        qr_data = {
            "page_id": page_id,
            "album_id": album_id
        }
        
        response = qr_client.post("/api/v1/qr/generate", json=qr_data, headers=headers)
        assert response.status_code == 201
        qr_code = response.json()
        
        # 5. Получаем публичный URL для альбома
        response = album_client.get(f"/api/v1/albums/{album_id}/public")
        assert response.status_code == 200
        public_album = response.json()
        
        assert public_album["id"] == album_id
        assert public_album["title"] == "Public Test Album"
        assert public_album["is_public"] is True
        
        # 6. Симулируем сканирование QR кода без авторизации
        # (В реальном приложении это было бы через scan-gateway)
        response = qr_client.post(
            f"/api/v1/qr/{qr_code['id']}/scan",
            json={"scanner_info": {"ip": "127.0.0.1", "user_agent": "test"}}
        )
        assert response.status_code == 200
        
        # 7. Проверяем, что можно получить информацию о странице без авторизации
        response = album_client.get(f"/api/v1/albums/{album_id}/pages/{page_id}/public")
        assert response.status_code == 200
        public_page = response.json()
        
        assert public_page["id"] == page_id
        assert public_page["title"] == "Public Page"
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_album_sharing_workflow(
        self,
        gateway_client: TestClient,
        auth_client: TestClient,
        album_client: TestClient,
        qr_client: TestClient
    ):
        """Тест процесса совместного использования альбома."""
        
        # 1. Создаем двух пользователей
        users = []
        for i in range(2):
            user_data = {
                "email": f"share{i}@example.com",
                "username": f"shareuser{i}",
                "password": "password123",
                "first_name": f"Share{i}",
                "last_name": "User"
            }
            
            response = auth_client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 201
            users.append(response.json())
        
        # 2. Первый пользователь создает альбом
        login_data = {
            "email": "share0@example.com",
            "password": "password123"
        }
        
        response = auth_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        owner_token = response.json()["access_token"]
        owner_headers = {"Authorization": f"Bearer {owner_token}"}
        
        album_data = {
            "title": "Shared Album",
            "description": "Album for sharing",
            "is_public": False
        }
        
        response = album_client.post("/api/v1/albums", json=album_data, headers=owner_headers)
        assert response.status_code == 201
        album_id = response.json()["id"]
        
        # 3. Создаем страницу
        page_data = {
            "title": "Shared Page",
            "content": "Content for sharing",
            "page_number": 1
        }
        
        response = album_client.post(
            f"/api/v1/albums/{album_id}/pages",
            json=page_data,
            headers=owner_headers
        )
        assert response.status_code == 201
        page_id = response.json()["id"]
        
        # 4. Генерируем QR код
        qr_data = {
            "page_id": page_id,
            "album_id": album_id
        }
        
        response = qr_client.post("/api/v1/qr/generate", json=qr_data, headers=owner_headers)
        assert response.status_code == 201
        qr_code = response.json()
        
        # 5. Второй пользователь пытается получить доступ к приватному альбому
        login_data = {
            "email": "share1@example.com",
            "password": "password123"
        }
        
        response = auth_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        viewer_token = response.json()["access_token"]
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}
        
        # Должен получить 403 Forbidden
        response = album_client.get(f"/api/v1/albums/{album_id}", headers=viewer_headers)
        assert response.status_code == 403
        
        # 6. Владелец делает альбом публичным
        update_data = {"is_public": True}
        response = album_client.put(
            f"/api/v1/albums/{album_id}",
            json=update_data,
            headers=owner_headers
        )
        assert response.status_code == 200
        
        # 7. Теперь второй пользователь может получить доступ
        response = album_client.get(f"/api/v1/albums/{album_id}", headers=viewer_headers)
        assert response.status_code == 200
        shared_album = response.json()
        
        assert shared_album["id"] == album_id
        assert shared_album["is_public"] is True
        
        # 8. Второй пользователь может сканировать QR код
        response = qr_client.post(
            f"/api/v1/qr/{qr_code['id']}/scan",
            json={"scanner_info": {"ip": "127.0.0.1", "user_agent": "test"}},
            headers=viewer_headers
        )
        assert response.status_code == 200
        
        # 9. Проверяем статистику сканирований
        response = qr_client.get(f"/api/v1/qr/{qr_code['id']}/stats", headers=owner_headers)
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["scan_count"] >= 1
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_error_handling_workflow(
        self,
        gateway_client: TestClient,
        auth_client: TestClient,
        album_client: TestClient
    ):
        """Тест обработки ошибок в полном рабочем процессе."""
        
        # 1. Попытка доступа без авторизации
        response = album_client.get("/api/v1/albums")
        assert response.status_code == 401
        
        # 2. Попытка входа с неверными данными
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = auth_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        
        # 3. Создаем пользователя
        user_data = {
            "email": "error@example.com",
            "username": "erroruser",
            "password": "password123",
            "first_name": "Error",
            "last_name": "User"
        }
        
        response = auth_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        # 4. Входим
        login_data = {
            "email": "error@example.com",
            "password": "password123"
        }
        
        response = auth_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 5. Попытка получить несуществующий альбом
        response = album_client.get("/api/v1/albums/999", headers=headers)
        assert response.status_code == 404
        
        # 6. Создаем альбом
        album_data = {
            "title": "Error Test Album",
            "description": "Album for error testing",
            "is_public": True
        }
        
        response = album_client.post("/api/v1/albums", json=album_data, headers=headers)
        assert response.status_code == 201
        album_id = response.json()["id"]
        
        # 7. Попытка создать страницу с неверными данными
        invalid_page_data = {
            "title": "",  # Пустое название
            "content": "Content",
            "page_number": -1  # Неверный номер страницы
        }
        
        response = album_client.post(
            f"/api/v1/albums/{album_id}/pages",
            json=invalid_page_data,
            headers=headers
        )
        assert response.status_code == 422  # Validation Error
        
        # 8. Попытка создать страницу в несуществующем альбоме
        page_data = {
            "title": "Valid Page",
            "content": "Valid Content",
            "page_number": 1
        }
        
        response = album_client.post(
            "/api/v1/albums/999/pages",
            json=page_data,
            headers=headers
        )
        assert response.status_code == 404
        
        # 9. Попытка обновить несуществующую страницу
        update_data = {"title": "Updated Title"}
        response = album_client.put(
            "/api/v1/pages/999",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 404
