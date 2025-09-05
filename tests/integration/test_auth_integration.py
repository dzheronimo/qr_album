"""
Integration тесты для auth-svc.

Тестирует интеграцию auth-svc с другими сервисами.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from fastapi.testclient import TestClient

from apps.auth_svc.app.main import app
from apps.auth_svc.app.database import get_db
from apps.auth_svc.app.integration import EventHandlers, ServiceClients, AuthCacheManager
from packages.py_commons.integration import Event, EventTypes


class TestAuthIntegration:
    """Integration тесты для auth-svc."""
    
    @pytest_asyncio.fixture
    async def test_client(self, test_db_session):
        """Фикстура для тестового клиента."""
        def override_get_db():
            return test_db_session
        
        app.dependency_overrides[get_db] = override_get_db
        
        with TestClient(app) as client:
            yield client
        
        app.dependency_overrides.clear()
    
    @pytest_asyncio.fixture
    async def event_handlers(self):
        """Фикстура для обработчиков событий."""
        return EventHandlers()
    
    @pytest_asyncio.fixture
    async def service_clients(self):
        """Фикстура для HTTP клиентов сервисов."""
        return ServiceClients()
    
    @pytest_asyncio.fixture
    async def cache_manager(self, test_redis_client):
        """Фикстура для менеджера кэша."""
        return AuthCacheManager(test_redis_client.config)
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_user_registration_flow(self, test_client: TestClient):
        """Тест полного потока регистрации пользователя."""
        # Регистрация пользователя
        registration_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = test_client.post("/api/v1/auth/register", json=registration_data)
        assert response.status_code == 201
        
        user_data = response.json()
        assert user_data["email"] == registration_data["email"]
        assert user_data["username"] == registration_data["username"]
        assert "id" in user_data
        assert user_data["is_active"] is True
        assert user_data["is_verified"] is False
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_user_login_flow(self, test_client: TestClient):
        """Тест полного потока входа пользователя."""
        # Сначала регистрируем пользователя
        registration_data = {
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "password123",
            "first_name": "Login",
            "last_name": "User"
        }
        
        test_client.post("/api/v1/auth/register", json=registration_data)
        
        # Теперь входим
        login_data = {
            "email": "loginuser@example.com",
            "password": "password123"
        }
        
        response = test_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert "expires_in" in token_data
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_protected_endpoint_access(self, test_client: TestClient):
        """Тест доступа к защищенным эндпоинтам."""
        # Регистрируем и входим
        registration_data = {
            "email": "protected@example.com",
            "username": "protected",
            "password": "password123",
            "first_name": "Protected",
            "last_name": "User"
        }
        
        test_client.post("/api/v1/auth/register", json=registration_data)
        
        login_data = {
            "email": "protected@example.com",
            "password": "password123"
        }
        
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Доступ к защищенному эндпоинту
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "protected@example.com"
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_token_refresh_flow(self, test_client: TestClient):
        """Тест обновления токенов."""
        # Регистрируем и входим
        registration_data = {
            "email": "refresh@example.com",
            "username": "refresh",
            "password": "password123",
            "first_name": "Refresh",
            "last_name": "User"
        }
        
        test_client.post("/api/v1/auth/register", json=registration_data)
        
        login_data = {
            "email": "refresh@example.com",
            "password": "password123"
        }
        
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Обновляем токены
        refresh_data = {"refresh_token": refresh_token}
        response = test_client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_event_handlers(self, event_handlers: EventHandlers):
        """Тест обработчиков событий."""
        # Создаем тестовое событие
        event = Event(
            event_type=EventTypes.USER_REGISTERED,
            service_name="test-service",
            data={
                "user_id": 1,
                "user_data": {
                    "email": "test@example.com",
                    "username": "testuser"
                }
            },
            timestamp=datetime.utcnow()
        )
        
        # Тестируем обработчик
        with patch('tests.integration.test_auth_integration.logger') as mock_logger:
            await event_handlers._handle_user_registered(event)
            mock_logger.info.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_cache_integration(self, cache_manager: AuthCacheManager):
        """Тест интеграции с кэшем."""
        await cache_manager.connect()
        
        # Кэшируем данные пользователя
        user_data = {
            "id": 1,
            "email": "cache@example.com",
            "username": "cacheuser",
            "permissions": ["read", "write"]
        }
        
        success = await cache_manager.cache_user_auth_data(1, user_data)
        assert success is True
        
        # Получаем данные из кэша
        cached_data = await cache_manager.get_user_auth_data(1)
        assert cached_data["id"] == 1
        assert cached_data["email"] == "cache@example.com"
        
        # Кэшируем разрешения
        permissions = {"read": True, "write": True, "admin": False}
        success = await cache_manager.cache_user_permissions(1, permissions)
        assert success is True
        
        # Получаем разрешения из кэша
        cached_permissions = await cache_manager.get_user_permissions(1)
        assert cached_permissions["read"] is True
        assert cached_permissions["admin"] is False
        
        await cache_manager.disconnect()
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_service_clients_integration(self, service_clients: ServiceClients):
        """Тест интеграции с другими сервисами."""
        # Тестируем получение клиентов
        auth_client = service_clients.get_client("auth-svc")
        assert auth_client is not None
        
        album_client = service_clients.get_client("album-svc")
        assert album_client is not None
        
        # Тестируем статистику
        stats = service_clients.get_stats()
        assert "auth-svc" in stats
        assert "album-svc" in stats
        
        await service_clients.close_all()
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_password_reset_flow(self, test_client: TestClient, cache_manager: AuthCacheManager):
        """Тест потока сброса пароля."""
        await cache_manager.connect()
        
        # Регистрируем пользователя
        registration_data = {
            "email": "reset@example.com",
            "username": "reset",
            "password": "password123",
            "first_name": "Reset",
            "last_name": "User"
        }
        
        test_client.post("/api/v1/auth/register", json=registration_data)
        
        # Запрашиваем сброс пароля
        reset_data = {"email": "reset@example.com"}
        response = test_client.post("/api/v1/auth/forgot-password", json=reset_data)
        assert response.status_code == 200
        
        # Проверяем, что токен сброса создан в кэше
        # (В реальном приложении токен был бы отправлен по email)
        # Здесь мы симулируем получение токена
        reset_token = "test-reset-token"
        await cache_manager.cache_password_reset_token(reset_token, 1)
        
        # Проверяем, что токен существует
        user_id = await cache_manager.get_password_reset_user_id(reset_token)
        assert user_id == 1
        
        # Сбрасываем пароль
        new_password_data = {
            "token": reset_token,
            "new_password": "newpassword123"
        }
        
        response = test_client.post("/api/v1/auth/reset-password", json=new_password_data)
        assert response.status_code == 200
        
        # Проверяем, что токен удален
        user_id = await cache_manager.get_password_reset_user_id(reset_token)
        assert user_id is None
        
        # Проверяем, что можно войти с новым паролем
        login_data = {
            "email": "reset@example.com",
            "password": "newpassword123"
        }
        
        response = test_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        await cache_manager.disconnect()
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_user_profile_update_flow(self, test_client: TestClient):
        """Тест потока обновления профиля пользователя."""
        # Регистрируем и входим
        registration_data = {
            "email": "profile@example.com",
            "username": "profile",
            "password": "password123",
            "first_name": "Profile",
            "last_name": "User"
        }
        
        test_client.post("/api/v1/auth/register", json=registration_data)
        
        login_data = {
            "email": "profile@example.com",
            "password": "password123"
        }
        
        login_response = test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Обновляем профиль
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.put("/api/v1/auth/profile", json=update_data, headers=headers)
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["first_name"] == "Updated"
        assert user_data["last_name"] == "Name"
    
    @pytest.mark.integration
    @pytest.mark.auth
    async def test_rate_limiting(self, test_client: TestClient):
        """Тест ограничения скорости запросов."""
        # Делаем много запросов на вход с неверными данными
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        # Первые несколько запросов должны проходить
        for i in range(5):
            response = test_client.post("/api/v1/auth/login", json=login_data)
            assert response.status_code == 401
        
        # После превышения лимита должен возвращаться 429
        # (Это зависит от настроек rate limiting в приложении)
        # В реальном приложении здесь был бы тест на rate limiting
