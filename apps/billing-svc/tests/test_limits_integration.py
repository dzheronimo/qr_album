"""
Интеграционные тесты для эндпоинтов лимитов.

Покрывает полный цикл работы с API эндпоинтами лимитов.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.main import app
from app.models.billing import Plan, Subscription, SubscriptionStatus, Usage


class TestLimitsEndpoints:
    """Тесты для эндпоинтов лимитов."""
    
    @pytest.fixture
    def client(self):
        """Тестовый клиент FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_plan(self):
        """Образец плана."""
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.name = "Basic"
        plan.max_albums = 5
        plan.max_pages_per_album = 50
        plan.max_storage_gb = 1
        return plan
    
    @pytest.fixture
    def sample_subscription(self):
        """Образец подписки."""
        subscription = MagicMock(spec=Subscription)
        subscription.id = 1
        subscription.user_id = 1
        subscription.plan_id = 1
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.end_date = None
        return subscription
    
    @pytest.fixture
    def sample_usage(self):
        """Образец использования."""
        usage = MagicMock(spec=Usage)
        usage.albums_count = 3
        usage.pages_count = 15
        usage.storage_used_mb = 450
        return usage
    
    @pytest.fixture
    def mock_db_session(self, sample_plan, sample_subscription, sample_usage):
        """Мок сессии базы данных."""
        mock_db = AsyncMock()
        
        # Настройка последовательности вызовов execute
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Третий вызов - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        return mock_db
    
    @patch('app.database.get_db')
    def test_get_limits_success(self, mock_get_db, client, mock_db_session):
        """Тест успешного получения лимитов."""
        mock_get_db.return_value = mock_db_session
        
        response = client.get("/limits?user_id=1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверка структуры ответа согласно API.md
        assert "albums" in data
        assert "pages" in data
        assert "storage" in data
        
        # Проверка альбомов
        albums = data["albums"]
        assert albums["used"] == 3
        assert albums["limit"] == 5
        assert albums["remaining"] == 2
        
        # Проверка страниц
        pages = data["pages"]
        assert pages["used"] == 15
        assert pages["limit"] == 50
        assert pages["remaining"] == 35
        
        # Проверка хранилища
        storage = data["storage"]
        assert storage["used_mb"] == 450
        assert storage["limit_mb"] == 1024  # 1 ГБ = 1024 МБ
        assert storage["remaining_mb"] == 574
    
    @patch('app.database.get_db')
    def test_get_limits_no_subscription(self, mock_get_db, client):
        """Тест получения лимитов без подписки."""
        mock_db = AsyncMock()
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_get_db.return_value = mock_db
        
        response = client.get("/limits?user_id=1")
        
        assert response.status_code == 404
        data = response.json()
        assert "У пользователя нет активной подписки" in data["detail"]
    
    @patch('app.database.get_db')
    def test_get_limits_unlimited_plan(self, mock_get_db, client):
        """Тест получения лимитов для безлимитного плана."""
        # Создаем безлимитный план
        unlimited_plan = MagicMock(spec=Plan)
        unlimited_plan.id = 2
        unlimited_plan.name = "Unlimited"
        unlimited_plan.max_albums = -1
        unlimited_plan.max_pages_per_album = -1
        unlimited_plan.max_storage_gb = -1
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 2
        
        # Создаем использование
        usage = MagicMock(spec=Usage)
        usage.albums_count = 100
        usage.pages_count = 500
        usage.storage_used_mb = 5000
        
        # Настройка моков
        mock_db = AsyncMock()
        mock_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=unlimited_plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        mock_get_db.return_value = mock_db
        
        response = client.get("/limits?user_id=1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверка безлимитных значений
        assert data["albums"]["limit"] == -1
        assert data["albums"]["remaining"] == -1
        assert data["pages"]["limit"] == -1
        assert data["pages"]["remaining"] == -1
        assert data["storage"]["limit_mb"] == -1
        assert data["storage"]["remaining_mb"] == -1
    
    @patch('app.database.get_db')
    def test_check_limits_success(self, mock_get_db, client, mock_db_session):
        """Тест успешной проверки лимитов для операции."""
        mock_get_db.return_value = mock_db_session
        
        request_data = {
            "albums_delta": 1,
            "pages_delta": 10,
            "storage_delta_mb": 100
        }
        
        response = client.post("/limits/check?user_id=1", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["can_proceed"] is True
        assert len(data["exceeded_limits"]) == 0
        assert data["message"] is None
        assert data["limits"] is not None
    
    @patch('app.database.get_db')
    def test_check_limits_exceeded(self, mock_get_db, client, mock_db_session):
        """Тест проверки лимитов при превышении."""
        mock_get_db.return_value = mock_db_session
        
        request_data = {
            "albums_delta": 5,  # Превышает лимит
            "pages_delta": 50,  # Превышает лимит
            "storage_delta_mb": 1000  # Превышает лимит
        }
        
        response = client.post("/limits/check?user_id=1", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["can_proceed"] is False
        assert len(data["exceeded_limits"]) == 3
        assert "Превышен лимит альбомов" in data["exceeded_limits"][0]
        assert "Превышен лимит страниц" in data["exceeded_limits"][1]
        assert "Превышен лимит хранилища" in data["exceeded_limits"][2]
        assert "Превышены лимиты тарифного плана" in data["message"]
    
    @patch('app.database.get_db')
    def test_check_limits_no_subscription(self, mock_get_db, client):
        """Тест проверки лимитов без подписки."""
        mock_db = AsyncMock()
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        mock_get_db.return_value = mock_db
        
        request_data = {
            "albums_delta": 1,
            "pages_delta": 10,
            "storage_delta_mb": 100
        }
        
        response = client.post("/limits/check?user_id=1", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["can_proceed"] is False
        assert len(data["exceeded_limits"]) == 0
        assert "У пользователя нет активной подписки" in data["message"]
    
    def test_get_limits_missing_user_id(self, client):
        """Тест получения лимитов без user_id."""
        response = client.get("/limits")
        
        assert response.status_code == 422  # Validation error
    
    def test_check_limits_missing_user_id(self, client):
        """Тест проверки лимитов без user_id."""
        request_data = {
            "albums_delta": 1,
            "pages_delta": 10,
            "storage_delta_mb": 100
        }
        
        response = client.post("/limits/check", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_check_limits_invalid_data(self, client):
        """Тест проверки лимитов с невалидными данными."""
        request_data = {
            "albums_delta": "invalid",  # Не число
            "pages_delta": -10,  # Отрицательное значение
            "storage_delta_mb": 100
        }
        
        response = client.post("/limits/check?user_id=1", json=request_data)
        
        assert response.status_code == 422  # Validation error


class TestLimitsEndpointsEdgeCases:
    """Тесты граничных случаев для эндпоинтов лимитов."""
    
    @pytest.fixture
    def client(self):
        """Тестовый клиент FastAPI."""
        return TestClient(app)
    
    @patch('app.database.get_db')
    def test_get_limits_with_none_values(self, mock_get_db, client):
        """Тест получения лимитов с None значениями в данных."""
        # Создаем план с None лимитами
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.max_albums = None
        plan.max_pages_per_album = None
        plan.max_storage_gb = None
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 1
        
        # Создаем использование с None значениями
        usage = MagicMock(spec=Usage)
        usage.albums_count = None
        usage.pages_count = None
        usage.storage_used_mb = None
        
        # Настройка моков
        mock_db = AsyncMock()
        mock_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        mock_get_db.return_value = mock_db
        
        response = client.get("/limits?user_id=1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверка, что None значения преобразованы корректно
        assert data["albums"]["used"] == 0
        assert data["albums"]["limit"] == -1  # Безлимит
        assert data["pages"]["used"] == 0
        assert data["pages"]["limit"] == -1  # Безлимит
        assert data["storage"]["used_mb"] == 0
        assert data["storage"]["limit_mb"] == -1  # Безлимит
    
    @patch('app.database.get_db')
    def test_check_limits_with_zero_deltas(self, mock_get_db, client):
        """Тест проверки лимитов с нулевыми дельтами."""
        # Создаем план
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.max_albums = 5
        plan.max_pages_per_album = 50
        plan.max_storage_gb = 1
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 1
        
        # Создаем использование
        usage = MagicMock(spec=Usage)
        usage.albums_count = 3
        usage.pages_count = 15
        usage.storage_used_mb = 450
        
        # Настройка моков
        mock_db = AsyncMock()
        mock_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        mock_get_db.return_value = mock_db
        
        request_data = {
            "albums_delta": 0,
            "pages_delta": 0,
            "storage_delta_mb": 0
        }
        
        response = client.post("/limits/check?user_id=1", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["can_proceed"] is True
        assert len(data["exceeded_limits"]) == 0
    
    @patch('app.database.get_db')
    def test_check_limits_with_negative_deltas(self, mock_get_db, client):
        """Тест проверки лимитов с отрицательными дельтами."""
        # Создаем план
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.max_albums = 5
        plan.max_pages_per_album = 50
        plan.max_storage_gb = 1
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 1
        
        # Создаем использование
        usage = MagicMock(spec=Usage)
        usage.albums_count = 3
        usage.pages_count = 15
        usage.storage_used_mb = 450
        
        # Настройка моков
        mock_db = AsyncMock()
        mock_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        mock_get_db.return_value = mock_db
        
        request_data = {
            "albums_delta": -1,  # Уменьшение
            "pages_delta": -5,   # Уменьшение
            "storage_delta_mb": -100  # Уменьшение
        }
        
        response = client.post("/limits/check?user_id=1", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Отрицательные дельты не должны вызывать превышение
        assert data["can_proceed"] is True
        assert len(data["exceeded_limits"]) == 0
