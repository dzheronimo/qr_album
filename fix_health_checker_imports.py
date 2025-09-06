#!/usr/bin/env python3
"""
Скрипт для исправления импортов health_checker во всех Python сервисах
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
    app_dir = f"apps/{service_name}/app"
    
    if not os.path.exists(app_dir):
        print(f"Директория {app_dir} не найдена")
        return
    
    # Находим все Python файлы
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_health_checker_in_file(file_path)

def fix_health_checker_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, есть ли неправильный импорт health_checker
        if 'health_router.dependency_overrides.get("health_checker")' in content:
            print(f"Исправляю health_checker в {file_path}")
            
            # Заменяем неправильный импорт
            content = re.sub(
                r'health_checker = health_router\.dependency_overrides\.get\("health_checker"\)\s*if health_checker:\s*health_checker\.add_dependency_check',
                '# Получаем health_checker из глобального состояния\nfrom health import _health_checker\nif _health_checker:\n    _health_checker.add_dependency_check',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            # Исправляем остальные вызовы health_checker
            content = re.sub(
                r'health_checker\.add_dependency_check',
                '_health_checker.add_dependency_check',
                content
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Исправлен {file_path}")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")

def main():
    print("Исправляю импорты health_checker во всех Python сервисах...")
    
    for service in services:
        print(f"\nОбрабатываю {service}...")
        fix_health_checker_in_service(service)
    
    print("\n✅ Все импорты health_checker исправлены!")

if __name__ == "__main__":
    main()
