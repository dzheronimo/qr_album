"""
Модели для работы с лимитами в формате API.md.

Содержит Pydantic v2 модели для корректной валидации и обработки лимитов.
"""

from typing import Optional, Literal, Union
from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from decimal import Decimal


class LimitInfo(BaseModel):
    """
    Информация о лимите ресурса.
    
    Поддерживает безлимитные значения (-1) и корректно вычисляет remaining.
    """
    
    used: int = Field(ge=0, description="Использованное количество")
    limit: Union[int, Literal[-1]] = Field(ge=-1, description="Лимит (-1 = безлимит)")
    
    @field_validator('used', mode='before')
    @classmethod
    def validate_used(cls, v):
        """Валидация и приведение used к int."""
        if v is None:
            return 0
        if isinstance(v, (str, Decimal)):
            try:
                return int(v)
            except (ValueError, TypeError):
                raise ValueError(f"Невозможно преобразовать {v} в int")
        if not isinstance(v, int):
            raise ValueError(f"used должен быть int, получен {type(v)}")
        if v < 0:
            raise ValueError("used не может быть отрицательным")
        return v
    
    @field_validator('limit', mode='before')
    @classmethod
    def validate_limit(cls, v):
        """Валидация и приведение limit к int или -1."""
        if v is None:
            raise ValueError("limit не может быть None")
        if isinstance(v, (str, Decimal)):
            try:
                parsed = int(v)
                if parsed < -1:
                    raise ValueError("limit не может быть меньше -1")
                return parsed
            except (ValueError, TypeError):
                raise ValueError(f"Невозможно преобразовать {v} в int")
        if not isinstance(v, int):
            raise ValueError(f"limit должен быть int, получен {type(v)}")
        if v < -1:
            raise ValueError("limit не может быть меньше -1")
        return v
    
    @model_validator(mode='after')
    def validate_used_vs_limit(self):
        """Проверка, что used не превышает limit (кроме безлимита)."""
        if self.limit != -1 and self.used > self.limit:
            raise ValueError(f"used ({self.used}) не может превышать limit ({self.limit})")
        return self
    
    @computed_field
    @property
    def remaining(self) -> Union[int, Literal[-1]]:
        """
        Вычисляет оставшееся количество.
        
        Returns:
            int: оставшееся количество (max(limit - used, 0))
            -1: если limit = -1 (безлимит)
        """
        if self.limit == -1:
            return -1  # Безлимит
        return max(self.limit - self.used, 0)
    
    def can_use(self, amount: int) -> bool:
        """
        Проверяет, можно ли использовать указанное количество.
        
        Args:
            amount: Количество для проверки
            
        Returns:
            bool: True если можно использовать
        """
        if amount < 0:
            return False
        if self.limit == -1:
            return True  # Безлимит
        return self.used + amount <= self.limit
    
    def get_remaining_for_use(self, amount: int) -> int:
        """
        Возвращает оставшееся количество после использования.
        
        Args:
            amount: Количество для использования
            
        Returns:
            int: оставшееся количество после использования
        """
        if self.limit == -1:
            return -1  # Безлимит
        return max(self.limit - (self.used + amount), 0)


class LimitsResponse(BaseModel):
    """
    Ответ с информацией о лимитах пользователя в формате API.md.
    
    Структура соответствует контракту:
    {
        "albums": {"used": 3, "limit": 5, "remaining": 2},
        "pages": {"used": 15, "limit": 50, "remaining": 35},
        "storage": {"used_mb": 45, "limit_mb": 100, "remaining_mb": 55}
    }
    """
    
    albums: LimitInfo = Field(description="Лимиты альбомов")
    pages: LimitInfo = Field(description="Лимиты страниц")
    storage: LimitInfo = Field(description="Лимиты хранилища")
    
    @model_validator(mode='after')
    def validate_limits(self):
        """Дополнительная валидация лимитов."""
        # Можно добавить бизнес-правила, например:
        # - если albums безлимит, то pages тоже должен быть безлимит
        return self


class StorageLimitInfo(BaseModel):
    """
    Информация о лимите хранилища в МБ.
    
    Отдельная модель для storage, так как у неё другие единицы измерения.
    """
    
    used_mb: int = Field(ge=0, description="Использованное хранилище в МБ")
    limit_mb: Union[int, Literal[-1]] = Field(ge=-1, description="Лимит хранилища в МБ (-1 = безлимит)")
    
    @field_validator('used_mb', mode='before')
    @classmethod
    def validate_used_mb(cls, v):
        """Валидация used_mb."""
        if v is None:
            return 0
        if isinstance(v, (str, Decimal)):
            try:
                return int(v)
            except (ValueError, TypeError):
                raise ValueError(f"Невозможно преобразовать {v} в int")
        if not isinstance(v, int):
            raise ValueError(f"used_mb должен быть int, получен {type(v)}")
        if v < 0:
            raise ValueError("used_mb не может быть отрицательным")
        return v
    
    @field_validator('limit_mb', mode='before')
    @classmethod
    def validate_limit_mb(cls, v):
        """Валидация limit_mb."""
        if v is None:
            raise ValueError("limit_mb не может быть None")
        if isinstance(v, (str, Decimal)):
            try:
                parsed = int(v)
                if parsed < -1:
                    raise ValueError("limit_mb не может быть меньше -1")
                return parsed
            except (ValueError, TypeError):
                raise ValueError(f"Невозможно преобразовать {v} в int")
        if not isinstance(v, int):
            raise ValueError(f"limit_mb должен быть int, получен {type(v)}")
        if v < -1:
            raise ValueError("limit_mb не может быть меньше -1")
        return v
    
    @model_validator(mode='after')
    def validate_used_vs_limit(self):
        """Проверка, что used_mb не превышает limit_mb (кроме безлимита)."""
        if self.limit_mb != -1 and self.used_mb > self.limit_mb:
            raise ValueError(f"used_mb ({self.used_mb}) не может превышать limit_mb ({self.limit_mb})")
        return self
    
    @computed_field
    @property
    def remaining_mb(self) -> Union[int, Literal[-1]]:
        """
        Вычисляет оставшееся хранилище в МБ.
        
        Returns:
            int: оставшееся количество в МБ (max(limit_mb - used_mb, 0))
            -1: если limit_mb = -1 (безлимит)
        """
        if self.limit_mb == -1:
            return -1  # Безлимит
        return max(self.limit_mb - self.used_mb, 0)
    
    def can_use(self, amount_mb: int) -> bool:
        """
        Проверяет, можно ли использовать указанное количество МБ.
        
        Args:
            amount_mb: Количество МБ для проверки
            
        Returns:
            bool: True если можно использовать
        """
        if amount_mb < 0:
            return False
        if self.limit_mb == -1:
            return True  # Безлимит
        return self.used_mb + amount_mb <= self.limit_mb


class LimitsResponseV2(BaseModel):
    """
    Ответ с информацией о лимитах пользователя в формате API.md (версия 2).
    
    Использует StorageLimitInfo для корректной работы с МБ.
    """
    
    albums: LimitInfo = Field(description="Лимиты альбомов")
    pages: LimitInfo = Field(description="Лимиты страниц")
    storage: StorageLimitInfo = Field(description="Лимиты хранилища")
    
    @model_validator(mode='after')
    def validate_limits(self):
        """Дополнительная валидация лимитов."""
        return self


# Утилиты для преобразования данных
def create_limit_info(used: Optional[int], limit: Optional[int]) -> LimitInfo:
    """
    Создает LimitInfo из сырых данных.
    
    Args:
        used: Использованное количество (может быть None)
        limit: Лимит (может быть None)
        
    Returns:
        LimitInfo: Валидированная информация о лимите
    """
    return LimitInfo(
        used=used or 0,
        limit=limit if limit is not None else -1
    )


def create_storage_limit_info(used_mb: Optional[int], limit_gb: Optional[int]) -> StorageLimitInfo:
    """
    Создает StorageLimitInfo из сырых данных.
    
    Args:
        used_mb: Использованное хранилище в МБ (может быть None)
        limit_gb: Лимит хранилища в ГБ (может быть None)
        
    Returns:
        StorageLimitInfo: Валидированная информация о лимите хранилища
    """
    limit_mb = limit_gb * 1024 if limit_gb is not None else -1
    return StorageLimitInfo(
        used_mb=used_mb or 0,
        limit_mb=limit_mb
    )
