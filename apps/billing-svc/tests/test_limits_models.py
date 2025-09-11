"""
Тесты для моделей лимитов.

Покрывает все сценарии валидации и вычислений в моделях лимитов.
"""

import pytest
from pydantic import ValidationError
from decimal import Decimal

from app.models.limits import (
    LimitInfo, 
    StorageLimitInfo, 
    LimitsResponseV2,
    create_limit_info,
    create_storage_limit_info
)


class TestLimitInfo:
    """Тесты для модели LimitInfo."""
    
    def test_valid_limit_info(self):
        """Тест создания валидной информации о лимите."""
        limit = LimitInfo(used=5, limit=10)
        assert limit.used == 5
        assert limit.limit == 10
        assert limit.remaining == 5
    
    def test_unlimited_limit(self):
        """Тест безлимитного лимита (-1)."""
        limit = LimitInfo(used=100, limit=-1)
        assert limit.used == 100
        assert limit.limit == -1
        assert limit.remaining == -1
    
    def test_zero_remaining(self):
        """Тест случая, когда лимит исчерпан."""
        limit = LimitInfo(used=10, limit=10)
        assert limit.remaining == 0
    
    def test_negative_remaining_handling(self):
        """Тест обработки отрицательного remaining."""
        limit = LimitInfo(used=15, limit=10)
        assert limit.remaining == 0  # max(10 - 15, 0) = 0
    
    def test_type_conversion_used(self):
        """Тест приведения типов для used."""
        # Строка
        limit = LimitInfo(used="5", limit=10)
        assert limit.used == 5
        
        # Decimal
        limit = LimitInfo(used=Decimal("5"), limit=10)
        assert limit.used == 5
        
        # None
        limit = LimitInfo(used=None, limit=10)
        assert limit.used == 0
    
    def test_type_conversion_limit(self):
        """Тест приведения типов для limit."""
        # Строка
        limit = LimitInfo(used=5, limit="10")
        assert limit.limit == 10
        
        # Decimal
        limit = LimitInfo(used=5, limit=Decimal("10"))
        assert limit.limit == 10
        
        # Безлимит
        limit = LimitInfo(used=5, limit="-1")
        assert limit.limit == -1
    
    def test_validation_errors(self):
        """Тест ошибок валидации."""
        # Отрицательный used
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used=-1, limit=10)
        assert "used не может быть отрицательным" in str(exc_info.value)
        
        # None limit
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used=5, limit=None)
        assert "limit не может быть None" in str(exc_info.value)
        
        # Limit меньше -1
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used=5, limit=-2)
        assert "limit не может быть меньше -1" in str(exc_info.value)
        
        # Used больше limit (кроме безлимита)
        with pytest.raises(ValidationError) as exc_info:
            LimitInfo(used=15, limit=10)
        assert "used (15) не может превышать limit (10)" in str(exc_info.value)
    
    def test_can_use_method(self):
        """Тест метода can_use."""
        limit = LimitInfo(used=5, limit=10)
        
        # Можно использовать
        assert limit.can_use(3) is True
        assert limit.can_use(5) is True  # Точно в лимит
        
        # Нельзя использовать
        assert limit.can_use(6) is False
        assert limit.can_use(-1) is False  # Отрицательное значение
        
        # Безлимит
        unlimited = LimitInfo(used=100, limit=-1)
        assert unlimited.can_use(1000) is True
        assert unlimited.can_use(-1) is False  # Отрицательное значение
    
    def test_get_remaining_for_use_method(self):
        """Тест метода get_remaining_for_use."""
        limit = LimitInfo(used=5, limit=10)
        
        # Нормальное использование
        assert limit.get_remaining_for_use(3) == 2  # 10 - (5 + 3) = 2
        assert limit.get_remaining_for_use(5) == 0  # 10 - (5 + 5) = 0
        
        # Превышение лимита
        assert limit.get_remaining_for_use(6) == 0  # max(10 - (5 + 6), 0) = 0
        
        # Безлимит
        unlimited = LimitInfo(used=100, limit=-1)
        assert unlimited.get_remaining_for_use(1000) == -1


class TestStorageLimitInfo:
    """Тесты для модели StorageLimitInfo."""
    
    def test_valid_storage_limit(self):
        """Тест создания валидной информации о лимите хранилища."""
        limit = StorageLimitInfo(used_mb=500, limit_mb=1024)
        assert limit.used_mb == 500
        assert limit.limit_mb == 1024
        assert limit.remaining_mb == 524
    
    def test_unlimited_storage(self):
        """Тест безлимитного хранилища."""
        limit = StorageLimitInfo(used_mb=5000, limit_mb=-1)
        assert limit.remaining_mb == -1
    
    def test_type_conversion_storage(self):
        """Тест приведения типов для хранилища."""
        # Строки
        limit = StorageLimitInfo(used_mb="500", limit_mb="1024")
        assert limit.used_mb == 500
        assert limit.limit_mb == 1024
        
        # Decimal
        limit = StorageLimitInfo(used_mb=Decimal("500"), limit_mb=Decimal("1024"))
        assert limit.used_mb == 500
        assert limit.limit_mb == 1024
        
        # None для used_mb
        limit = StorageLimitInfo(used_mb=None, limit_mb=1024)
        assert limit.used_mb == 0
    
    def test_validation_errors_storage(self):
        """Тест ошибок валидации для хранилища."""
        # Отрицательный used_mb
        with pytest.raises(ValidationError) as exc_info:
            StorageLimitInfo(used_mb=-1, limit_mb=1024)
        assert "used_mb не может быть отрицательным" in str(exc_info.value)
        
        # None limit_mb
        with pytest.raises(ValidationError) as exc_info:
            StorageLimitInfo(used_mb=500, limit_mb=None)
        assert "limit_mb не может быть None" in str(exc_info.value)
        
        # Used_mb больше limit_mb
        with pytest.raises(ValidationError) as exc_info:
            StorageLimitInfo(used_mb=1500, limit_mb=1024)
        assert "used_mb (1500) не может превышать limit_mb (1024)" in str(exc_info.value)


class TestLimitsResponseV2:
    """Тесты для модели LimitsResponseV2."""
    
    def test_valid_limits_response(self):
        """Тест создания валидного ответа с лимитами."""
        albums = LimitInfo(used=3, limit=5)
        pages = LimitInfo(used=15, limit=50)
        storage = StorageLimitInfo(used_mb=450, limit_mb=1024)
        
        response = LimitsResponseV2(
            albums=albums,
            pages=pages,
            storage=storage
        )
        
        assert response.albums.remaining == 2
        assert response.pages.remaining == 35
        assert response.storage.remaining_mb == 574
    
    def test_unlimited_plan(self):
        """Тест плана с безлимитными ресурсами."""
        albums = LimitInfo(used=100, limit=-1)
        pages = LimitInfo(used=500, limit=-1)
        storage = StorageLimitInfo(used_mb=5000, limit_mb=-1)
        
        response = LimitsResponseV2(
            albums=albums,
            pages=pages,
            storage=storage
        )
        
        assert response.albums.remaining == -1
        assert response.pages.remaining == -1
        assert response.storage.remaining_mb == -1


class TestUtilityFunctions:
    """Тесты для утилитарных функций."""
    
    def test_create_limit_info(self):
        """Тест функции create_limit_info."""
        # Нормальные значения
        limit = create_limit_info(used=5, limit=10)
        assert limit.used == 5
        assert limit.limit == 10
        
        # None значения
        limit = create_limit_info(used=None, limit=None)
        assert limit.used == 0
        assert limit.limit == -1  # Безлимит по умолчанию
    
    def test_create_storage_limit_info(self):
        """Тест функции create_storage_limit_info."""
        # Нормальные значения (ГБ в МБ)
        limit = create_storage_limit_info(used_mb=500, limit_gb=1)
        assert limit.used_mb == 500
        assert limit.limit_mb == 1024  # 1 ГБ = 1024 МБ
        
        # None значения
        limit = create_storage_limit_info(used_mb=None, limit_gb=None)
        assert limit.used_mb == 0
        assert limit.limit_mb == -1  # Безлимит по умолчанию


class TestEdgeCases:
    """Тесты граничных случаев."""
    
    def test_zero_values(self):
        """Тест нулевых значений."""
        limit = LimitInfo(used=0, limit=0)
        assert limit.remaining == 0
        assert limit.can_use(0) is True
        assert limit.can_use(1) is False
    
    def test_large_numbers(self):
        """Тест больших чисел."""
        limit = LimitInfo(used=1000000, limit=2000000)
        assert limit.remaining == 1000000
        assert limit.can_use(500000) is True
        assert limit.can_use(1500000) is False
    
    def test_string_edge_cases(self):
        """Тест граничных случаев со строками."""
        # Пустая строка
        with pytest.raises(ValidationError):
            LimitInfo(used="", limit=10)
        
        # Невалидная строка
        with pytest.raises(ValidationError):
            LimitInfo(used="abc", limit=10)
        
        # Строка с плавающей точкой
        with pytest.raises(ValidationError):
            LimitInfo(used="5.5", limit=10)  # Должно быть целое число
