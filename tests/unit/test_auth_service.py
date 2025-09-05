"""
Unit тесты для auth-svc.

Тестирует бизнес-логику сервиса аутентификации.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth_svc.app.services.auth_service import AuthService
from apps.auth_svc.app.models.user import User, UserRole
from apps.auth_svc.app.schemas.user import UserCreate, UserLogin, UserUpdate


class TestAuthService:
    """Тесты для AuthService."""
    
    @pytest_asyncio.fixture
    async def auth_service(self, test_db_session: AsyncSession):
        """Фикстура для AuthService."""
        return AuthService(test_db_session)
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_create_user_success(self, auth_service: AuthService, test_user_data: dict):
        """Тест успешного создания пользователя."""
        user_data = UserCreate(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password="testpassword123",
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"]
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            user = await auth_service.create_user(user_data)
            
            assert user.email == test_user_data["email"]
            assert user.username == test_user_data["username"]
            assert user.first_name == test_user_data["first_name"]
            assert user.last_name == test_user_data["last_name"]
            assert user.is_active is True
            assert user.is_verified is False
            mock_hash.assert_called_once_with("testpassword123")
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_create_user_duplicate_email(self, auth_service: AuthService):
        """Тест создания пользователя с дублирующимся email."""
        # Создаем первого пользователя
        user_data1 = UserCreate(
            email="test@example.com",
            username="user1",
            password="password123",
            first_name="User",
            last_name="One"
        )
        
        await auth_service.create_user(user_data1)
        
        # Пытаемся создать второго пользователя с тем же email
        user_data2 = UserCreate(
            email="test@example.com",
            username="user2",
            password="password123",
            first_name="User",
            last_name="Two"
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.create_user(user_data2)
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_user_success(self, auth_service: AuthService):
        """Тест успешной аутентификации пользователя."""
        # Создаем пользователя
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.create_user(user_data)
        
        # Аутентифицируем пользователя
        login_data = UserLogin(
            email="test@example.com",
            password="testpassword123"
        )
        
        with patch.object(auth_service, '_verify_password') as mock_verify:
            mock_verify.return_value = True
            
            authenticated_user = await auth_service.authenticate_user(login_data)
            
            assert authenticated_user.id == user.id
            assert authenticated_user.email == user.email
            mock_verify.assert_called_once_with("testpassword123", "hashed_password")
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_authenticate_user_invalid_credentials(self, auth_service: AuthService):
        """Тест аутентификации с неверными учетными данными."""
        login_data = UserLogin(
            email="nonexistent@example.com",
            password="wrongpassword"
        )
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.authenticate_user(login_data)
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_generate_tokens(self, auth_service: AuthService, test_user_data: dict):
        """Тест генерации токенов."""
        user = User(
            id=test_user_data["id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            is_active=test_user_data["is_active"],
            is_verified=test_user_data["is_verified"]
        )
        
        with patch.object(auth_service, '_create_access_token') as mock_access, \
             patch.object(auth_service, '_create_refresh_token') as mock_refresh:
            
            mock_access.return_value = "access_token"
            mock_refresh.return_value = "refresh_token"
            
            tokens = await auth_service.generate_tokens(user)
            
            assert tokens["access_token"] == "access_token"
            assert tokens["refresh_token"] == "refresh_token"
            assert tokens["token_type"] == "bearer"
            assert "expires_in" in tokens
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_refresh_tokens_success(self, auth_service: AuthService, test_user_data: dict):
        """Тест успешного обновления токенов."""
        user = User(
            id=test_user_data["id"],
            email=test_user_data["email"],
            username=test_user_data["username"],
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            is_active=test_user_data["is_active"],
            is_verified=test_user_data["is_verified"]
        )
        
        with patch.object(auth_service, '_verify_refresh_token') as mock_verify, \
             patch.object(auth_service, '_create_access_token') as mock_access, \
             patch.object(auth_service, '_create_refresh_token') as mock_refresh:
            
            mock_verify.return_value = user
            mock_access.return_value = "new_access_token"
            mock_refresh.return_value = "new_refresh_token"
            
            tokens = await auth_service.refresh_tokens("valid_refresh_token")
            
            assert tokens["access_token"] == "new_access_token"
            assert tokens["refresh_token"] == "new_refresh_token"
            mock_verify.assert_called_once_with("valid_refresh_token")
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_refresh_tokens_invalid(self, auth_service: AuthService):
        """Тест обновления токенов с неверным refresh токеном."""
        with patch.object(auth_service, '_verify_refresh_token') as mock_verify:
            mock_verify.return_value = None
            
            with pytest.raises(ValueError, match="Invalid refresh token"):
                await auth_service.refresh_tokens("invalid_refresh_token")
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_update_user_success(self, auth_service: AuthService, test_user_data: dict):
        """Тест успешного обновления пользователя."""
        # Создаем пользователя
        user_data = UserCreate(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password="testpassword123",
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"]
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.create_user(user_data)
        
        # Обновляем пользователя
        update_data = UserUpdate(
            first_name="Updated",
            last_name="Name"
        )
        
        updated_user = await auth_service.update_user(user.id, update_data)
        
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.email == test_user_data["email"]  # Не изменился
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_update_user_not_found(self, auth_service: AuthService):
        """Тест обновления несуществующего пользователя."""
        update_data = UserUpdate(first_name="Updated")
        
        with pytest.raises(ValueError, match="User not found"):
            await auth_service.update_user(999, update_data)
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_deactivate_user(self, auth_service: AuthService, test_user_data: dict):
        """Тест деактивации пользователя."""
        # Создаем пользователя
        user_data = UserCreate(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password="testpassword123",
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"]
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.create_user(user_data)
        
        # Деактивируем пользователя
        await auth_service.deactivate_user(user.id)
        
        # Проверяем, что пользователь деактивирован
        deactivated_user = await auth_service.get_user_by_id(user.id)
        assert deactivated_user.is_active is False
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_verify_email(self, auth_service: AuthService, test_user_data: dict):
        """Тест верификации email."""
        # Создаем пользователя
        user_data = UserCreate(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password="testpassword123",
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"]
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.create_user(user_data)
        
        # Верифицируем email
        await auth_service.verify_email(user.id)
        
        # Проверяем, что email верифицирован
        verified_user = await auth_service.get_user_by_id(user.id)
        assert verified_user.is_verified is True
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_get_user_by_id(self, auth_service: AuthService, test_user_data: dict):
        """Тест получения пользователя по ID."""
        # Создаем пользователя
        user_data = UserCreate(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password="testpassword123",
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"]
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.create_user(user_data)
        
        # Получаем пользователя по ID
        found_user = await auth_service.get_user_by_id(user.id)
        
        assert found_user.id == user.id
        assert found_user.email == user.email
        assert found_user.username == user.username
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_get_user_by_email(self, auth_service: AuthService, test_user_data: dict):
        """Тест получения пользователя по email."""
        # Создаем пользователя
        user_data = UserCreate(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password="testpassword123",
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"]
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.create_user(user_data)
        
        # Получаем пользователя по email
        found_user = await auth_service.get_user_by_email(user.email)
        
        assert found_user.id == user.id
        assert found_user.email == user.email
        assert found_user.username == user.username
    
    @pytest.mark.unit
    @pytest.mark.auth
    async def test_get_user_by_username(self, auth_service: AuthService, test_user_data: dict):
        """Тест получения пользователя по username."""
        # Создаем пользователя
        user_data = UserCreate(
            email=test_user_data["email"],
            username=test_user_data["username"],
            password="testpassword123",
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"]
        )
        
        with patch.object(auth_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            user = await auth_service.create_user(user_data)
        
        # Получаем пользователя по username
        found_user = await auth_service.get_user_by_username(user.username)
        
        assert found_user.id == user.id
        assert found_user.email == user.email
        assert found_user.username == user.username
