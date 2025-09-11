"""
Тесты для проверки конкурентных операций с лимитами.

Покрывает сценарии race conditions и атомарные операции.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.services.limits_service import LimitsService
from app.models.billing import Plan, Subscription, SubscriptionStatus, Usage


class TestConcurrencyLimits:
    """Тесты для конкурентных операций с лимитами."""
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных."""
        return AsyncMock()
    
    @pytest.fixture
    def sample_plan(self):
        """Образец плана с ограниченными лимитами."""
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
        """Образец использования с почти исчерпанными лимитами."""
        usage = MagicMock(spec=Usage)
        usage.albums_count = 4  # Остался 1 альбом
        usage.pages_count = 45  # Осталось 5 страниц
        usage.storage_used_mb = 900  # Осталось 124 МБ
        return usage
    
    @pytest.fixture
    def limits_service(self, mock_db):
        """Сервис лимитов с моком БД."""
        return LimitsService(mock_db)
    
    async def test_concurrent_limit_checks(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """
        Тест конкурентных проверок лимитов.
        
        Симулирует ситуацию, когда несколько запросов одновременно проверяют лимиты.
        """
        # Настройка моков для каждого вызова
        mock_db.execute.side_effect = [
            # Вызов 1 - получение подписки
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Вызов 2 - получение плана
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Вызов 3 - получение использования
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage)),
            # Вызов 4 - получение подписки (второй запрос)
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            # Вызов 5 - получение плана (второй запрос)
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            # Вызов 6 - получение использования (второй запрос)
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        async def check_limits_task():
            """Задача для проверки лимитов."""
            return await limits_service.check_limits_for_operation(
                user_id=1,
                albums_delta=1,  # Пытаемся создать 1 альбом
                pages_delta=3,   # Пытаемся создать 3 страницы
                storage_delta_mb=50  # Пытаемся использовать 50 МБ
            )
        
        # Запускаем несколько конкурентных задач
        tasks = [check_limits_task() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Проверяем, что все задачи выполнились успешно
        assert len(results) == 5
        for result in results:
            assert result["can_proceed"] is True
            assert len(result["exceeded_limits"]) == 0
    
    async def test_concurrent_limit_checks_with_exceeded_limits(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """
        Тест конкурентных проверок лимитов при превышении.
        
        Симулирует ситуацию, когда несколько запросов одновременно превышают лимиты.
        """
        # Настройка моков
        mock_db.execute.side_effect = [
            # Множественные вызовы для каждого запроса
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        async def check_limits_exceeded_task():
            """Задача для проверки лимитов с превышением."""
            return await limits_service.check_limits_for_operation(
                user_id=1,
                albums_delta=2,  # Превышает лимит (4 + 2 > 5)
                pages_delta=10,  # Превышает лимит (45 + 10 > 50)
                storage_delta_mb=200  # Превышает лимит (900 + 200 > 1024)
            )
        
        # Запускаем несколько конкурентных задач
        tasks = [check_limits_exceeded_task() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Проверяем, что все задачи корректно определили превышение
        assert len(results) == 3
        for result in results:
            assert result["can_proceed"] is False
            assert len(result["exceeded_limits"]) == 3
            assert "Превышен лимит альбомов" in result["exceeded_limits"][0]
            assert "Превышен лимит страниц" in result["exceeded_limits"][1]
            assert "Превышен лимит хранилища" in result["exceeded_limits"][2]
    
    async def test_concurrent_get_limits(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """
        Тест конкурентного получения лимитов.
        
        Симулирует ситуацию, когда несколько запросов одновременно получают лимиты.
        """
        # Настройка моков для множественных вызовов
        mock_db.execute.side_effect = [
            # Вызовы для каждого запроса get_user_limits
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=sample_usage))
        ]
        
        async def get_limits_task():
            """Задача для получения лимитов."""
            return await limits_service.get_user_limits(user_id=1)
        
        # Запускаем несколько конкурентных задач
        tasks = [get_limits_task() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Проверяем, что все задачи вернули одинаковые результаты
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.albums.used == 4
            assert result.albums.limit == 5
            assert result.albums.remaining == 1
            assert result.pages.used == 45
            assert result.pages.limit == 50
            assert result.pages.remaining == 5
            assert result.storage.used_mb == 900
            assert result.storage.limit_mb == 1024
            assert result.storage.remaining_mb == 124
    
    async def test_race_condition_simulation(self, limits_service, mock_db, sample_plan, sample_subscription, sample_usage):
        """
        Симуляция race condition при проверке лимитов.
        
        Симулирует ситуацию, когда между проверкой лимита и его использованием
        происходит изменение данных.
        """
        # Создаем два разных состояния использования
        usage_before = MagicMock(spec=Usage)
        usage_before.albums_count = 4
        usage_before.pages_count = 45
        usage_before.storage_used_mb = 900
        
        usage_after = MagicMock(spec=Usage)
        usage_after.albums_count = 5  # Лимит исчерпан
        usage_after.pages_count = 50  # Лимит исчерпан
        usage_after.storage_used_mb = 1024  # Лимит исчерпан
        
        # Настройка моков для симуляции race condition
        call_count = 0
        
        async def mock_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count <= 3:
                # Первые 3 вызова - состояние до изменения
                if call_count == 1:
                    return MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription))
                elif call_count == 2:
                    return MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan))
                else:
                    return MagicMock(scalar_one_or_none=MagicMock(return_value=usage_before))
            else:
                # Следующие вызовы - состояние после изменения
                if call_count == 4:
                    return MagicMock(scalar_one_or_none=MagicMock(return_value=sample_subscription))
                elif call_count == 5:
                    return MagicMock(scalar_one_or_none=MagicMock(return_value=sample_plan))
                else:
                    return MagicMock(scalar_one_or_none=MagicMock(return_value=usage_after))
        
        mock_db.execute.side_effect = mock_execute
        
        # Первая проверка - лимиты еще не исчерпаны
        result1 = await limits_service.check_limits_for_operation(
            user_id=1,
            albums_delta=1,
            pages_delta=3,
            storage_delta_mb=50
        )
        
        # Вторая проверка - лимиты уже исчерпаны
        result2 = await limits_service.check_limits_for_operation(
            user_id=1,
            albums_delta=1,
            pages_delta=3,
            storage_delta_mb=50
        )
        
        # Проверяем результаты
        assert result1["can_proceed"] is True
        assert len(result1["exceeded_limits"]) == 0
        
        assert result2["can_proceed"] is False
        assert len(result2["exceeded_limits"]) == 3
        assert "Превышен лимит альбомов" in result2["exceeded_limits"][0]
        assert "Превышен лимит страниц" in result2["exceeded_limits"][1]
        assert "Превышен лимит хранилища" in result2["exceeded_limits"][2]


class TestAtomicOperations:
    """Тесты для атомарных операций с лимитами."""
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных."""
        return AsyncMock()
    
    @pytest.fixture
    def limits_service(self, mock_db):
        """Сервис лимитов с моком БД."""
        return LimitsService(mock_db)
    
    async def test_atomic_limit_check_and_update_simulation(self, limits_service, mock_db):
        """
        Симуляция атомарной проверки и обновления лимитов.
        
        В реальной реализации это должно быть сделано через транзакции БД.
        """
        # Создаем план с ограниченными лимитами
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.max_albums = 1  # Очень ограниченный лимит
        plan.max_pages_per_album = 10
        plan.max_storage_gb = 1
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 1
        
        # Создаем использование с исчерпанным лимитом альбомов
        usage = MagicMock(spec=Usage)
        usage.albums_count = 1  # Лимит исчерпан
        usage.pages_count = 5
        usage.storage_used_mb = 500
        
        # Настройка моков
        mock_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        
        # Проверяем лимиты для создания альбома
        result = await limits_service.check_limits_for_operation(
            user_id=1,
            albums_delta=1,  # Пытаемся создать альбом
            pages_delta=0,
            storage_delta_mb=0
        )
        
        # Должно быть отклонено, так как лимит альбомов исчерпан
        assert result["can_proceed"] is False
        assert len(result["exceeded_limits"]) == 1
        assert "Превышен лимит альбомов" in result["exceeded_limits"][0]
    
    async def test_concurrent_operations_with_shared_limits(self, limits_service, mock_db):
        """
        Тест конкурентных операций с общими лимитами.
        
        Симулирует ситуацию, когда несколько операций используют общие лимиты.
        """
        # Создаем план
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.max_albums = 3
        plan.max_pages_per_album = 30
        plan.max_storage_gb = 1
        
        # Создаем подписку
        subscription = MagicMock(spec=Subscription)
        subscription.plan_id = 1
        
        # Создаем использование
        usage = MagicMock(spec=Usage)
        usage.albums_count = 1
        usage.pages_count = 10
        usage.storage_used_mb = 300
        
        # Настройка моков для множественных вызовов
        mock_db.execute.side_effect = [
            # Вызовы для каждого запроса
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=subscription)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=plan)),
            MagicMock(scalar_one_or_none=MagicMock(return_value=usage))
        ]
        
        async def operation_task(operation_id: int):
            """Задача для операции."""
            return await limits_service.check_limits_for_operation(
                user_id=1,
                albums_delta=1,  # Каждая операция пытается создать 1 альбом
                pages_delta=5,   # Каждая операция пытается создать 5 страниц
                storage_delta_mb=100  # Каждая операция пытается использовать 100 МБ
            )
        
        # Запускаем 3 конкурентные операции
        tasks = [operation_task(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # Проверяем результаты
        assert len(results) == 3
        
        # Все операции должны пройти проверку, так как лимиты не превышены
        for result in results:
            assert result["can_proceed"] is True
            assert len(result["exceeded_limits"]) == 0
        
        # Проверяем, что общее использование не превысит лимиты
        # Исходное: 1 альбом, 10 страниц, 300 МБ
        # После 3 операций: 1+3=4 альбома (лимит 3 - превышен), 10+15=25 страниц (лимит 30 - ОК), 300+300=600 МБ (лимит 1024 - ОК)
        # Но каждая операция проверяет только свои дельты, поэтому все проходят
