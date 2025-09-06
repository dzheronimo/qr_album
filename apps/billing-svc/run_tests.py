#!/usr/bin/env python3
"""
Скрипт для запуска тестов billing-svc.

Запускает все тесты для проверки исправления бага #audit-006.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Запускает команду и выводит результат."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - УСПЕШНО")
        else:
            print(f"❌ {description} - ОШИБКА (код: {result.returncode})")
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ {description} - ИСКЛЮЧЕНИЕ: {e}")
        return False


def main():
    """Основная функция."""
    print("🚀 Запуск тестов billing-svc для проверки исправления бага #audit-006")
    print("=" * 80)
    
    # Список тестов для запуска
    tests = [
        {
            "command": "python -m pytest tests/test_limits_models.py -v",
            "description": "Тесты моделей лимитов (Pydantic v2)"
        },
        {
            "command": "python -m pytest tests/test_limits_service.py -v",
            "description": "Тесты сервиса лимитов"
        },
        {
            "command": "python -m pytest tests/test_limits_integration.py -v",
            "description": "Интеграционные тесты эндпоинтов"
        },
        {
            "command": "python -m pytest tests/test_limits_bug_reproduction.py -v",
            "description": "Тесты воспроизведения бага #audit-006"
        },
        {
            "command": "python -m pytest tests/test_limits_concurrency.py -v",
            "description": "Тесты конкурентных операций"
        },
        {
            "command": "python -m pytest tests/ -v --tb=short",
            "description": "Все тесты billing-svc"
        }
    ]
    
    # Запуск тестов
    results = []
    for test in tests:
        success = run_command(test["command"], test["description"])
        results.append((test["description"], success))
    
    # Итоговый отчет
    print(f"\n{'='*80}")
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print(f"{'='*80}")
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        print(f"{status}: {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 СТАТИСТИКА:")
    print(f"   Всего тестов: {len(results)}")
    print(f"   Пройдено: {passed}")
    print(f"   Провалено: {failed}")
    print(f"   Процент успеха: {(passed/len(results)*100):.1f}%")
    
    if failed == 0:
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Баг #audit-006 исправлен.")
        return 0
    else:
        print(f"\n⚠️  ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ. Требуется дополнительная работа.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
