"""
Тесты для сервиса лимитов.

Покрывает бизнес-логику работы с лимитами пользователей.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.services.limits_service import LimitsService
from app.models.billing import Plan, Subscription, SubscriptionStatus, Usage
from app.models.limits import LimitsResponseV2


class TestLimitsService:
    """Тесты для сервиса лимитов."""
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных."""
        return AsyncMock()
    
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
    def limits_service(self, mock_db):
        """Сервис лимитов с моком БД."""
        return LimitsService(mock_db)
    
    async def test_get_user_limits_success(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """Тест успешного получения лимитов пользователя."""
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Третий вызов - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        # Вызов метода
        result = await limits_service.get_user_limits(user_id=1)
        
        # Проверки
        assert isinstance(result, LimitsResponseV2)
        assert result.albums.used == 3
        assert result.albums.limit == 5
        assert result.albums.remaining == 2
        assert result.pages.used == 15
        assert result.pages.limit == 50
        assert result.pages.remaining == 35
        assert result.storage.used_mb == 450
        assert result.storage.limit_mb == 1024  # 1 ГБ = 1024 МБ
        assert result.storage.remaining_mb == 574
    
    async def test_get_user_limits_no_subscription(self, limits_service, mock_db):
        """Тест получения лимитов без подписки."""
        # Настройка мока - нет подписки
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        
        # Проверка исключения
        with pytest.raises(ValueError, match="У пользователя нет активной подписки"):
            await limits_service.get_user_limits(user_id=1)
    
    async def test_get_user_limits_no_plan(self, limits_service, mock_db, sample_subscription):
        """Тест получения лимитов без плана."""
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана (None)
            MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        ]
        
        # Проверка исключения
        with pytest.raises(ValueError, match="План подписки не найден"):
            await limits_service.get_user_limits(user_id=1)
    
    async def test_get_user_limits_no_usage(self, limits_service, mock_db, sample_plan, sample_subscription):
        """Тест получения лимитов без данных об использовании."""
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Третий вызов - получение использования (None)
            MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        ]
        
        # Вызов метода
        result = await limits_service.get_user_limits(user_id=1)
        
        # Проверки - все значения должны быть 0
        assert result.albums.used == 0
        assert result.pages.used == 0
        assert result.storage.used_mb == 0
    
    async def test_get_user_limits_unlimited_plan(self, limits_service, mock_db, sample_subscription, sample_usage):
        """Тест получения лимитов для безлимитного плана."""
        # Создаем безлимитный план
        unlimited_plan = MagicMock(spec=Plan)
        unlimited_plan.id = 2
        unlimited_plan.name = "Unlimited"
        unlimited_plan.max_albums = -1
        unlimited_plan.max_pages_per_album = -1
        unlimited_plan.max_storage_gb = -1
        
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=unlimited_plan)),
            # Третий вызов - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        # Вызов метода
        result = await limits_service.get_user_limits(user_id=1)
        
        # Проверки - все лимиты должны быть безлимитными
        assert result.albums.limit == -1
        assert result.albums.remaining == -1
        assert result.pages.limit == -1
        assert result.pages.remaining == -1
        assert result.storage.limit_mb == -1
        assert result.storage.remaining_mb == -1
    
    async def test_check_limits_for_operation_success(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """Тест успешной проверки лимитов для операции."""
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Третий вызов - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        # Вызов метода
        result = await limits_service.check_limits_for_operation(
            user_id=1,
            albums_delta=1,
            pages_delta=10,
            storage_delta_mb=100
        )
        
        # Проверки
        assert result["can_proceed"] is True
        assert len(result["exceeded_limits"]) == 0
        assert result["message"] is None
        assert result["limits"] is not None
    
    async def test_check_limits_for_operation_exceeded(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """Тест проверки лимитов при превышении."""
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Третий вызов - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        # Вызов метода с превышением лимитов
        result = await limits_service.check_limits_for_operation(
            user_id=1,
            albums_delta=5,  # Превышает лимит (3 + 5 > 5)
            pages_delta=50,  # Превышает лимит (15 + 50 > 50)
            storage_delta_mb=1000  # Превышает лимит (450 + 1000 > 1024)
        )
        
        # Проверки
        assert result["can_proceed"] is False
        assert len(result["exceeded_limits"]) == 3
        assert "Превышен лимит альбомов" in result["exceeded_limits"][0]
        assert "Превышен лимит страниц" in result["exceeded_limits"][1]
        assert "Превышен лимит хранилища" in result["exceeded_limits"][2]
        assert "Превышены лимиты тарифного плана" in result["message"]
    
    async def test_check_limits_for_operation_no_subscription(self, limits_service, mock_db):
        """Тест проверки лимитов без подписки."""
        # Настройка мока - нет подписки
        mock_db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))
        
        # Вызов метода
        result = await limits_service.check_limits_for_operation(user_id=1)
        
        # Проверки
        assert result["can_proceed"] is False
        assert len(result["exceeded_limits"]) == 0
        assert "У пользователя нет активной подписки" in result["message"]
    
    async def test_check_limits_for_operation_negative_deltas(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """Тест проверки лимитов с отрицательными дельтами (уменьшение использования)."""
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Третий вызов - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        # Вызов метода с отрицательными дельтами
        result = await limits_service.check_limits_for_operation(
            user_id=1,
            albums_delta=-1,  # Уменьшение
            pages_delta=-5,   # Уменьшение
            storage_delta_mb=-100  # Уменьшение
        )
        
        # Проверки - отрицательные дельты не должны вызывать превышение
        assert result["can_proceed"] is True
        assert len(result["exceeded_limits"]) == 0
    
    async def test_check_limits_for_operation_zero_deltas(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """Тест проверки лимитов с нулевыми дельтами."""
        # Настройка моков
        mock_db.execute.side_effect = [
            # Первый вызов - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Второй вызов - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Третий вызов - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        # Вызов метода с нулевыми дельтами
        result = await limits_service.check_limits_for_operation(user_id=1)
        
        # Проверки
        assert result["can_proceed"] is True
        assert len(result["exceeded_limits"]) == 0


class TestLimitsServiceEdgeCases:
    """Тесты граничных случаев для сервиса лимитов."""
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных."""
        return AsyncMock()
    
    @pytest.fixture
    def limits_service(self, mock_db):
        """Сервис лимитов с моком БД."""
        return LimitsService(mock_db)
    
    async def test_get_user_limits_with_none_values_in_usage(self, limits_service, mock_db):
        """Тест получения лимитов с None значениями в использовании."""
        # Создаем план
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.max_albums = 5
        plan.max_pages_per_album = 50
        plan.max_storage_gb = 1
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 1
        
        # Создаем использование с None значениями
        usage = MagicMock(spec=Usage)
        usage.albums_count = None
        usage.pages_count = None
        usage.storage_used_mb = None
        
        # Настройка моков
        mock_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        
        # Вызов метода
        result = await limits_service.get_user_limits(user_id=1)
        
        # Проверки - None значения должны быть преобразованы в 0
        assert result.albums.used == 0
        assert result.pages.used == 0
        assert result.storage.used_mb == 0
    
    async def test_get_user_limits_with_none_limits_in_plan(self, limits_service, mock_db):
        """Тест получения лимитов с None лимитами в плане."""
        # Создаем план с None лимитами
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.max_albums = None
        plan.max_pages_per_album = None
        plan.max_storage_gb = None
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 1
        
        # Создаем использование
        usage = MagicMock(spec=Usage)
        usage.albums_count = 3
        usage.pages_count = 15
        usage.storage_used_mb = 450
        
        # Настройка моков
        mock_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        
        # Вызов метода
        result = await limits_service.get_user_limits(user_id=1)
        
        # Проверки - None лимиты должны быть преобразованы в -1 (безлимит)
        assert result.albums.limit == -1
        assert result.pages.limit == -1
        assert result.storage.limit_mb == -1
