"""
Unit тесты для UsageService.

Тестирует исправление бага с проверкой лимитов.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.services.usage_service import UsageService
from app.models.billing import Usage, Plan, Subscription, SubscriptionStatus, PlanType


class TestUsageServiceLimits:
    """Тесты для проверки лимитов в UsageService."""
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных."""
        return AsyncMock()
    
    @pytest.fixture
    def usage_service(self, mock_db):
        """Экземпляр UsageService с мок БД."""
        return UsageService(mock_db)
    
    @pytest.fixture
    def sample_plan(self):
        """Образец плана."""
        plan = MagicMock(spec=Plan)
        plan.id = 1
        plan.name = "Basic"
        plan.max_albums = 10
        plan.max_pages_per_album = 50
        plan.max_media_files = 100
        plan.max_qr_codes = 200
        plan.max_storage_gb = 5
        plan.to_dict.return_value = {
            "id": 1,
            "name": "Basic",
            "max_albums": 10,
            "max_pages_per_album": 50,
            "max_media_files": 100,
            "max_qr_codes": 200,
            "max_storage_gb": 5
        }
        return plan
    
    @pytest.fixture
    def sample_subscription(self):
        """Образец подписки."""
        subscription = MagicMock(spec=Subscription)
        subscription.user_id = 1
        subscription.plan_id = 1
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.end_date = None
        return subscription
    
    @pytest.mark.asyncio
    async def test_check_limits_with_none_current_usage(self, usage_service, mock_db, sample_plan, sample_subscription):
        """Тест проверки лимитов когда current_usage = None."""
        # Настраиваем моки
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [sample_subscription, sample_plan]
        usage_service.get_current_usage = AsyncMock(return_value=None)
        
        # Вызываем метод
        result = await usage_service.check_limits(
            user_id=1,
            albums_count=5,
            pages_count=10
        )
        
        # Проверяем результат
        assert result["has_subscription"] is True
        assert result["limits_exceeded"] is False
        assert result["can_proceed"] is True
        assert len(result["exceeded_limits"]) == 0
    
    @pytest.mark.asyncio
    async def test_check_limits_with_none_values_in_usage(self, usage_service, mock_db, sample_plan, sample_subscription):
        """Тест проверки лимитов когда поля current_usage содержат None."""
        # Создаём current_usage с None значениями
        current_usage = MagicMock(spec=Usage)
        current_usage.albums_count = None
        current_usage.pages_count = 5
        current_usage.media_files_count = None
        current_usage.qr_codes_count = 10
        current_usage.storage_used_mb = None
        current_usage.to_dict.return_value = {
            "albums_count": None,
            "pages_count": 5,
            "media_files_count": None,
            "qr_codes_count": 10,
            "storage_used_mb": None
        }
        
        # Настраиваем моки
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [sample_subscription, sample_plan]
        usage_service.get_current_usage = AsyncMock(return_value=current_usage)
        
        # Вызываем метод
        result = await usage_service.check_limits(
            user_id=1,
            albums_count=8,  # 0 (None) + 8 = 8 < 10 (лимит)
            pages_count=40,  # 5 + 40 = 45 < 50 (лимит)
            media_files_count=50,  # 0 (None) + 50 = 50 < 100 (лимит)
            qr_codes_count=100,  # 10 + 100 = 110 < 200 (лимит)
            storage_used_mb=2000  # 0 (None) + 2000 = 2000MB = 2GB < 5GB (лимит)
        )
        
        # Проверяем результат
        assert result["has_subscription"] is True
        assert result["limits_exceeded"] is False
        assert result["can_proceed"] is True
        assert len(result["exceeded_limits"]) == 0
    
    @pytest.mark.asyncio
    async def test_check_limits_exceeded_with_none_values(self, usage_service, mock_db, sample_plan, sample_subscription):
        """Тест проверки лимитов с превышением когда поля содержат None."""
        # Создаём current_usage с None значениями
        current_usage = MagicMock(spec=Usage)
        current_usage.albums_count = None
        current_usage.pages_count = 45
        current_usage.media_files_count = None
        current_usage.qr_codes_count = 190
        current_usage.storage_used_mb = None
        current_usage.to_dict.return_value = {
            "albums_count": None,
            "pages_count": 45,
            "media_files_count": None,
            "qr_codes_count": 190,
            "storage_used_mb": None
        }
        
        # Настраиваем моки
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [sample_subscription, sample_plan]
        usage_service.get_current_usage = AsyncMock(return_value=current_usage)
        
        # Вызываем метод с превышением лимитов
        result = await usage_service.check_limits(
            user_id=1,
            albums_count=15,  # 0 (None) + 15 = 15 > 10 (лимит) - ПРЕВЫШЕНИЕ
            pages_count=10,   # 45 + 10 = 55 > 50 (лимит) - ПРЕВЫШЕНИЕ
            media_files_count=50,  # 0 (None) + 50 = 50 < 100 (лимит)
            qr_codes_count=20,  # 190 + 20 = 210 > 200 (лимит) - ПРЕВЫШЕНИЕ
            storage_used_mb=3000  # 0 (None) + 3000 = 3000MB = 3GB < 5GB (лимит)
        )
        
        # Проверяем результат
        assert result["has_subscription"] is True
        assert result["limits_exceeded"] is True
        assert result["can_proceed"] is False
        assert len(result["exceeded_limits"]) == 3
        
        # Проверяем конкретные превышения
        exceeded_limits = result["exceeded_limits"]
        assert any("альбомов: 15/10" in limit for limit in exceeded_limits)
        assert any("страниц: 55/50" in limit for limit in exceeded_limits)
        assert any("QR кодов: 210/200" in limit for limit in exceeded_limits)
    
    @pytest.mark.asyncio
    async def test_check_limits_no_subscription(self, usage_service, mock_db):
        """Тест проверки лимитов без подписки."""
        # Настраиваем моки - нет подписки
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        # Вызываем метод
        result = await usage_service.check_limits(
            user_id=1,
            albums_count=5
        )
        
        # Проверяем результат
        assert result["has_subscription"] is False
        assert result["limits_exceeded"] is True
        assert result["can_proceed"] is False
        assert result["message"] == "У пользователя нет активной подписки"
    
    @pytest.mark.asyncio
    async def test_check_limits_no_plan(self, usage_service, mock_db, sample_subscription):
        """Тест проверки лимитов без плана."""
        # Настраиваем моки - есть подписка, но нет плана
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [sample_subscription, None]
        
        # Вызываем метод
        result = await usage_service.check_limits(
            user_id=1,
            albums_count=5
        )
        
        # Проверяем результат
        assert result["has_subscription"] is False
        assert result["limits_exceeded"] is True
        assert result["can_proceed"] is False
        assert result["message"] == "План подписки не найден"


class TestCheckLimitsRequestValidation:
    """Тесты валидации CheckLimitsRequest."""
    
    def test_valid_positive_values(self):
        """Тест валидации положительных значений."""
        from app.routes.usage import CheckLimitsRequest
        
        # Валидные значения
        request = CheckLimitsRequest(
            albums_count=5,
            pages_count=10,
            media_files_count=20,
            qr_codes_count=15,
            storage_used_mb=100
        )
        
        assert request.albums_count == 5
        assert request.pages_count == 10
        assert request.media_files_count == 20
        assert request.qr_codes_count == 15
        assert request.storage_used_mb == 100
    
    def test_valid_none_values(self):
        """Тест валидации None значений."""
        from app.routes.usage import CheckLimitsRequest
        
        # None значения должны проходить валидацию
        request = CheckLimitsRequest(
            albums_count=None,
            pages_count=None,
            media_files_count=None,
            qr_codes_count=None,
            storage_used_mb=None
        )
        
        assert request.albums_count is None
        assert request.pages_count is None
        assert request.media_files_count is None
        assert request.qr_codes_count is None
        assert request.storage_used_mb is None
    
    def test_valid_zero_values(self):
        """Тест валидации нулевых значений."""
        from app.routes.usage import CheckLimitsRequest
        
        # Нулевые значения должны проходить валидацию
        request = CheckLimitsRequest(
            albums_count=0,
            pages_count=0,
            media_files_count=0,
            qr_codes_count=0,
            storage_used_mb=0
        )
        
        assert request.albums_count == 0
        assert request.pages_count == 0
        assert request.media_files_count == 0
        assert request.qr_codes_count == 0
        assert request.storage_used_mb == 0
    
    def test_invalid_negative_values(self):
        """Тест валидации отрицательных значений."""
        from app.routes.usage import CheckLimitsRequest
        from pydantic import ValidationError
        
        # Отрицательные значения должны вызывать ValidationError
        with pytest.raises(ValidationError) as exc_info:
            CheckLimitsRequest(albums_count=-1)
        
        assert "Значение не может быть отрицательным" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            CheckLimitsRequest(
                albums_count=5,
                pages_count=-10,
                media_files_count=20
            )
        
        assert "Значение не может быть отрицательным" in str(exc_info.value)
    
    def test_mixed_valid_values(self):
        """Тест валидации смешанных значений."""
        from app.routes.usage import CheckLimitsRequest
        
        # Смешанные валидные значения
        request = CheckLimitsRequest(
            albums_count=5,
            pages_count=None,
            media_files_count=0,
            qr_codes_count=None,
            storage_used_mb=100
        )
        
        assert request.albums_count == 5
        assert request.pages_count is None
        assert request.media_files_count == 0
        assert request.qr_codes_count is None
        assert request.storage_used_mb == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
