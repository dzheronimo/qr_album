"""
Тесты для воспроизведения и исправления бага #audit-006.

Покрывает конкретные случаи из ERROR_REGISTER.md и TODO.md п. 8.6.
"""

import pytest
from pydantic import ValidationError
from decimal import Decimal

from app.models.limits import LimitInfo, StorageLimitInfo, LimitsResponseV2
from app.services.limits_service import LimitsService
from app.models.billing import Plan, Subscription, SubscriptionStatus, Usage


class TestBugReproduction:
    """Тесты для воспроизведения бага с проверкой лимитов."""
    
    def test_pydantic_validation_bug_reproduction(self):
        """
        Воспроизведение бага из ERROR_REGISTER.md #audit-006.
        
        Проблема: "Проблема с проверкой лимитов (Pydantic)"
        """
        # Тест 1: Проверка, что валидация работает корректно
        # (этот тест должен проходить после исправления)
        
        # Нормальные значения
        limit = LimitInfo(used=5, limit=10)
        assert limit.used == 5
        assert limit.limit == 10
        assert limit.remaining == 5
        
        # None значения (должны обрабатываться корректно)
        limit = LimitInfo(used=None, limit=10)
        assert limit.used == 0  # None преобразуется в 0
        
        # Отрицательные значения (должны вызывать ошибку валидации)
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used=-1, limit=10)
        assert "used не может быть отрицательным" in str(exc_info.value)
        
        # Превышение лимита (должно вызывать ошибку валидации)
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used=15, limit=10)
        assert "used (15) не может превышать limit (10)" in str(exc_info.value)
    
    def test_type_conversion_bug_reproduction(self):
        """
        Воспроизведение проблемы с приведением типов.
        
        Проблема из TODO.md п. 8.6: "незначительная проблема с Pydantic"
        """
        # Тест приведения строк к числам
        limit = LimitInfo(used="5", limit="10")
        assert limit.used == 5
        assert limit.limit == 10
        
        # Тест приведения Decimal к int
        limit = LimitInfo(used=Decimal("5"), limit=Decimal("10"))
        assert limit.used == 5
        assert limit.limit == 10
        
        # Тест обработки невалидных строк
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used="abc", limit=10)
        assert "Невозможно преобразовать abc в int" in str(exc_info.value)
        
        # Тест обработки строк с плавающей точкой
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used="5.5", limit=10)
        assert "Невозможно преобразовать 5.5 в int" in str(exc_info.value)
    
    def test_unlimited_handling_bug_reproduction(self):
        """
        Воспроизведение проблемы с обработкой безлимитных значений.
        
        Проблема: неправильная обработка -1 (безлимит)
        """
        # Тест безлимитного лимита
        limit = LimitInfo(used=100, limit=-1)
        assert limit.limit == -1
        assert limit.remaining == -1
        assert limit.can_use(1000) is True  # Безлимит позволяет любое использование
        
        # Тест вычисления remaining для безлимита
        assert limit.get_remaining_for_use(500) == -1
        
        # Тест валидации: used может превышать limit только если limit = -1
        limit = LimitInfo(used=1000, limit=-1)
        assert limit.used == 1000
        assert limit.limit == -1
    
    def test_storage_limit_bug_reproduction(self):
        """
        Воспроизведение проблемы с лимитами хранилища.
        
        Проблема: неправильное преобразование ГБ в МБ
        """
        # Тест преобразования ГБ в МБ
        storage = StorageLimitInfo(used_mb=500, limit_mb=1024)  # 1 ГБ = 1024 МБ
        assert storage.used_mb == 500
        assert storage.limit_mb == 1024
        assert storage.remaining_mb == 524
        
        # Тест безлимитного хранилища
        storage = StorageLimitInfo(used_mb=5000, limit_mb=-1)
        assert storage.remaining_mb == -1
        
        # Тест валидации превышения лимита хранилища
        with pytest.raises(ValidationError) as exc_info:
            StorageLimitInfo(used_mb=1500, limit_mb=1024)
        assert "used_mb (1500) не может превышать limit_mb (1024)" in str(exc_info.value)
    
    def test_edge_cases_bug_reproduction(self):
        """
        Воспроизведение граничных случаев.
        
        Проблема: неправильная обработка граничных значений
        """
        # Тест нулевых значений
        limit = LimitInfo(used=0, limit=0)
        assert limit.remaining == 0
        assert limit.can_use(0) is True
        assert limit.can_use(1) is False
        
        # Тест случая, когда used = limit
        limit = LimitInfo(used=10, limit=10)
        assert limit.remaining == 0
        assert limit.can_use(0) is True
        assert limit.can_use(1) is False
        
        # Тест случая, когда used > limit (должно вызывать ошибку)
        with pytest.raises(ValidationError):
            LimitInfo(used=15, limit=10)
        
        # Тест больших чисел
        limit = LimitInfo(used=1000000, limit=2000000)
        assert limit.remaining == 1000000
        assert limit.can_use(500000) is True
        assert limit.can_use(1500000) is False


class TestBugFixes:
    """Тесты для проверки исправлений багов."""
    
    def test_none_handling_fix(self):
        """
        Проверка исправления обработки None значений.
        
        Исправление: None значения теперь корректно преобразуются в 0 или -1
        """
        # None для used должен преобразовываться в 0
        limit = LimitInfo(used=None, limit=10)
        assert limit.used == 0
        
        # None для limit должен вызывать ошибку (требуется явное указание)
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used=5, limit=None)
        assert "limit не может быть None" in str(exc_info.value)
    
    def test_type_safety_fix(self):
        """
        Проверка исправления типовой безопасности.
        
        Исправление: добавлена строгая типизация и валидация
        """
        # Проверка, что только int и совместимые типы принимаются
        limit = LimitInfo(used=5, limit=10)
        assert isinstance(limit.used, int)
        assert isinstance(limit.limit, int)
        
        # Проверка, что несовместимые типы отклоняются
        with pytest.raises(ValidationError):
            LimitInfo(used=[1, 2, 3], limit=10)
        
        with pytest.raises(ValidationError):
            LimitInfo(used={"count": 5}, limit=10)
    
    def test_business_logic_fix(self):
        """
        Проверка исправления бизнес-логики.
        
        Исправление: корректная обработка безлимитных планов
        """
        # Создание безлимитного плана
        unlimited_plan = LimitInfo(used=1000, limit=-1)
        
        # Проверка, что безлимитный план позволяет любое использование
        assert unlimited_plan.can_use(10000) is True
        assert unlimited_plan.can_use(100000) is True
        
        # Проверка, что remaining всегда -1 для безлимита
        assert unlimited_plan.remaining == -1
        assert unlimited_plan.get_remaining_for_use(5000) == -1
    
    def test_api_contract_compliance_fix(self):
        """
        Проверка соответствия контракту API.md.
        
        Исправление: структура ответа соответствует API.md
        """
        # Создание ответа в формате API.md
        albums = LimitInfo(used=3, limit=5)
        pages = LimitInfo(used=15, limit=50)
        storage = StorageLimitInfo(used_mb=450, limit_mb=1024)
        
        response = LimitsResponseV2(
            albums=albums,
            pages=pages,
            storage=storage
        )
        
        # Проверка структуры ответа
        data = response.model_dump()
        
        # Проверка альбомов
        assert "used" in data["albums"]
        assert "limit" in data["albums"]
        assert "remaining" in data["albums"]
        assert data["albums"]["used"] == 3
        assert data["albums"]["limit"] == 5
        assert data["albums"]["remaining"] == 2
        
        # Проверка страниц
        assert "used" in data["pages"]
        assert "limit" in data["pages"]
        assert "remaining" in data["pages"]
        assert data["pages"]["used"] == 15
        assert data["pages"]["limit"] == 50
        assert data["pages"]["remaining"] == 35
        
        # Проверка хранилища
        assert "used_mb" in data["storage"]
        assert "limit_mb" in data["storage"]
        assert "remaining_mb" in data["storage"]
        assert data["storage"]["used_mb"] == 450
        assert data["storage"]["limit_mb"] == 1024
        assert data["storage"]["remaining_mb"] == 574


class TestRegressionTests:
    """Регрессионные тесты для предотвращения повторного появления багов."""
    
    def test_original_bug_scenarios(self):
        """
        Тестирование сценариев из оригинального бага.
        
        Убеждаемся, что исправления не сломали существующую функциональность.
        """
        # Сценарий 1: Нормальное использование
        limit = LimitInfo(used=5, limit=10)
        assert limit.remaining == 5
        assert limit.can_use(3) is True
        assert limit.can_use(6) is False
        
        # Сценарий 2: Исчерпанный лимит
        limit = LimitInfo(used=10, limit=10)
        assert limit.remaining == 0
        assert limit.can_use(0) is True
        assert limit.can_use(1) is False
        
        # Сценарий 3: Безлимитный план
        limit = LimitInfo(used=100, limit=-1)
        assert limit.remaining == -1
        assert limit.can_use(1000) is True
        
        # Сценарий 4: Хранилище
        storage = StorageLimitInfo(used_mb=500, limit_mb=1024)
        assert storage.remaining_mb == 524
        assert storage.can_use(500) is True
        assert storage.can_use(600) is False
    
    def test_error_handling_regression(self):
        """
        Проверка, что обработка ошибок работает корректно.
        """
        # Отрицательные значения
        with pytest.raises(ValidationError):
            LimitInfo(used=-1, limit=10)
        
        with pytest.raises(ValidationError):
            StorageLimitInfo(used_mb=-1, limit_mb=1024)
        
        # Превышение лимитов
        with pytest.raises(ValidationError):
            LimitInfo(used=15, limit=10)
        
        with pytest.raises(ValidationError):
            StorageLimitInfo(used_mb=1500, limit_mb=1024)
        
        # Невалидные типы
        with pytest.raises(ValidationError):
            LimitInfo(used="abc", limit=10)
        
        with pytest.raises(ValidationError):
            StorageLimitInfo(used_mb="xyz", limit_mb=1024)
