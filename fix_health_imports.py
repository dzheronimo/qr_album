#!/usr/bin/env python3
"""
Скрипт для исправления импортов health модуля
"""

import os
import re

# Список всех Python сервисов
services = [
    'api-gateway',
    'auth-svc',
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

def fix_health_imports_in_service(service_name):
    app_dir = f"apps/{service_name}/app"
    
    if not os.path.exists(app_dir):
        print(f"Директория {app_dir} не найдена")
        return
    
    # Находим все Python файлы
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_health_imports_in_file(file_path)

def fix_health_imports_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Исправляем импорты health
        content = re.sub(
            r'from commons\.health import',
            'from health import',
            content
        )
        
        content = re.sub(
            r'import commons\.health',
            'import health',
            content
        )
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Исправлен {file_path}")
    
    except Exception as e:
        print(f"Ошибка при обработке {file_path}: {e}")

if __name__ == "__main__":
    for service in services:
        print(f"Обрабатываю {service}...")
        fix_health_imports_in_service(service)
    
    print("Все импорты health исправлены!")
