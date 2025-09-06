#!/usr/bin/env python3
"""
Тест для воспроизведения и анализа бага с проверкой лимитов в billing-svc.

Этот скрипт поможет выявить проблему с Pydantic валидацией.
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent / "app"))

from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, Any, List


class CheckLimitsRequest(BaseModel):
    """Запрос на проверку лимитов."""
    albums_count: Optional[int] = Field(None, ge=0, description="Количество альбомов для проверки")
    pages_count: Optional[int] = Field(None, ge=0, description="Количество страниц для проверки")
    media_files_count: Optional[int] = Field(None, ge=0, description="Количество медиафайлов для проверки")
    qr_codes_count: Optional[int] = Field(None, ge=0, description="Количество QR кодов для проверки")
    storage_used_mb: Optional[int] = Field(None, ge=0, description="Использованное хранилище в МБ для проверки")


class LimitsCheckResponse(BaseModel):
    """Ответ с результатом проверки лимитов."""
    has_subscription: bool
    plan: Optional[Dict[str, Any]] = None
    current_usage: Optional[Dict[str, Any]] = None
    limits_exceeded: bool
    exceeded_limits: List[str] = []
    can_proceed: bool
    message: Optional[str] = None


def test_pydantic_validation():
    """Тестирует Pydantic валидацию для выявления проблем."""
    
    print("🔍 Тестирование Pydantic валидации...")
    
    # Тест 1: Нормальные значения
    try:
        request1 = CheckLimitsRequest(
            albums_count=5,
            pages_count=10,
            media_files_count=20,
            qr_codes_count=15,
            storage_used_mb=100
        )
        print("✅ Тест 1 (нормальные значения): PASSED")
        print(f"   albums_count: {request1.albums_count}")
        print(f"   pages_count: {request1.pages_count}")
    except ValidationError as e:
        print(f"❌ Тест 1 (нормальные значения): FAILED - {e}")
    
    # Тест 2: None значения
    try:
        request2 = CheckLimitsRequest(
            albums_count=None,
            pages_count=None,
            media_files_count=None,
            qr_codes_count=None,
            storage_used_mb=None
        )
        print("✅ Тест 2 (None значения): PASSED")
        print(f"   albums_count: {request2.albums_count}")
    except ValidationError as e:
        print(f"❌ Тест 2 (None значения): FAILED - {e}")
    
    # Тест 3: Отрицательные значения
    try:
        request3 = CheckLimitsRequest(
            albums_count=-1,
            pages_count=-5,
            media_files_count=-10
        )
        print("❌ Тест 3 (отрицательные значения): FAILED - валидация не сработала!")
        print(f"   albums_count: {request3.albums_count}")
    except ValidationError as e:
        print("✅ Тест 3 (отрицательные значения): PASSED - валидация сработала")
        print(f"   Ошибка: {e}")
    
    # Тест 4: Нулевые значения
    try:
        request4 = CheckLimitsRequest(
            albums_count=0,
            pages_count=0,
            media_files_count=0
        )
        print("✅ Тест 4 (нулевые значения): PASSED")
        print(f"   albums_count: {request4.albums_count}")
    except ValidationError as e:
        print(f"❌ Тест 4 (нулевые значения): FAILED - {e}")
    
    # Тест 5: Смешанные значения
    try:
        request5 = CheckLimitsRequest(
            albums_count=5,
            pages_count=None,
            media_files_count=0,
            qr_codes_count=None,
            storage_used_mb=100
        )
        print("✅ Тест 5 (смешанные значения): PASSED")
        print(f"   albums_count: {request5.albums_count}")
        print(f"   pages_count: {request5.pages_count}")
        print(f"   media_files_count: {request5.media_files_count}")
    except ValidationError as e:
        print(f"❌ Тест 5 (смешанные значения): FAILED - {e}")


def test_response_model():
    """Тестирует модель ответа."""
    
    print("\n🔍 Тестирование модели ответа...")
    
    # Тест 1: Полный ответ
    try:
        response1 = LimitsCheckResponse(
            has_subscription=True,
            plan={"id": 1, "name": "Basic"},
            current_usage={"albums_count": 5},
            limits_exceeded=False,
            exceeded_limits=[],
            can_proceed=True,
            message=None
        )
        print("✅ Тест ответа 1 (полный): PASSED")
    except ValidationError as e:
        print(f"❌ Тест ответа 1 (полный): FAILED - {e}")
    
    # Тест 2: Минимальный ответ
    try:
        response2 = LimitsCheckResponse(
            has_subscription=False,
            limits_exceeded=True,
            can_proceed=False
        )
        print("✅ Тест ответа 2 (минимальный): PASSED")
    except ValidationError as e:
        print(f"❌ Тест ответа 2 (минимальный): FAILED - {e}")


def analyze_potential_issues():
    """Анализирует потенциальные проблемы в коде."""
    
    print("\n🔍 Анализ потенциальных проблем...")
    
    issues = []
    
    # Проблема 1: Проверка типов в check_limits
    print("1. Проверка типов в методе check_limits:")
    print("   - Параметры могут быть None, но код не всегда это учитывает")
    print("   - Нет проверки на отрицательные значения после валидации Pydantic")
    
    # Проблема 2: Логика проверки лимитов
    print("2. Логика проверки лимитов:")
    print("   - Строка 260: current_albums = (current_usage.albums_count if current_usage else 0) + albums_count")
    print("   - Если albums_count = None, то получится None + число = TypeError")
    
    # Проблема 3: Обработка None значений
    print("3. Обработка None значений:")
    print("   - В строках 259-283 есть проверки 'if albums_count is not None'")
    print("   - Но если albums_count = None, то сложение может вызвать ошибку")
    
    # Проблема 4: Валидация Pydantic
    print("4. Валидация Pydantic:")
    print("   - Field(ge=0) должна предотвращать отрицательные значения")
    print("   - Но None значения проходят валидацию")
    
    return issues


def main():
    """Основная функция."""
    print("🚀 Анализ бага billing-svc: проверка лимитов")
    print("=" * 50)
    
    test_pydantic_validation()
    test_response_model()
    analyze_potential_issues()
    
    print("\n🎯 Выводы:")
    print("1. Pydantic валидация работает корректно")
    print("2. Проблема может быть в логике обработки None значений")
    print("3. Нужно проверить метод check_limits на обработку None")
    print("4. Возможна проблема с типами данных при сложении")


if __name__ == "__main__":
    main()
