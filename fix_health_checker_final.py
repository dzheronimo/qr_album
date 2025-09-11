#!/usr/bin/env python3
"""
Скрипт для финального исправления health_checker во всех Python сервисах
"""

import os
import re

# Список всех Python сервисов
services = [
    'album-svc',
    'media-svc',
    'qr-svc',
    'user-profile-svc',
    'analytics-svc',
    'billing-svc',
    'notification-svc',
    'moderation-svc',
    'print-svc',
    'scan-gateway'
]

def fix_health_checker_in_service(service_name):
    health_file = f"apps/{service_name}/app/routes/health.py"
    
    if not os.path.exists(health_file):
        print(f"Файл {health_file} не найден")
        return
    
    try:
        with open(health_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Исправляю {health_file}")
        
        # Полностью переписываем секцию с health_checker
        # Находим начало секции с проверками зависимостей
        start_marker = "# Добавляем проверки зависимостей"
        end_marker = "# Включаем health endpoints"
        
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print(f"Не найдены маркеры в {health_file}")
            return
        
        # Извлекаем переменные окружения
        database_url_line = ""
        redis_url_line = ""
        rabbitmq_url_line = ""
        
        lines = content[start_idx:end_idx].split('\n')
        for line in lines:
            if 'database_url = os.getenv' in line:
                database_url_line = line.strip()
            elif 'redis_url = os.getenv' in line:
                redis_url_line = line.strip()
            elif 'rabbitmq_url = os.getenv' in line:
                rabbitmq_url_line = line.strip()
        
        # Создаем правильную секцию
        new_section = f"""# Добавляем проверки зависимостей
{database_url_line}
{redis_url_line}
{rabbitmq_url_line}

# Получаем health_checker из глобального состояния
from health import _health_checker
if _health_checker:
    _health_checker.add_dependency_check(lambda: check_database(database_url))
    _health_checker.add_dependency_check(lambda: check_redis(redis_url))
    _health_checker.add_dependency_check(lambda: check_rabbitmq(rabbitmq_url))

"""
        
        # Заменяем секцию
        new_content = content[:start_idx] + new_section + content[end_idx:]
        
        with open(health_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"✅ Исправлен {health_file}")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {health_file}: {e}")

def main():
    print("Финальное исправление health_checker во всех Python сервисах...")
    
    for service in services:
        print(f"\nОбрабатываю {service}...")
        fix_health_checker_in_service(service)
    
    print("\n✅ Все health_checker исправлены!")

if __name__ == "__main__":
    main()
