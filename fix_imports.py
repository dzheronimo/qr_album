#!/usr/bin/env python3
"""
Скрипт для исправления импортов py_commons во всех Python сервисах
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

def fix_imports_in_service(service_name):
    app_dir = f"apps/{service_name}/app"
    
    if not os.path.exists(app_dir):
        print(f"Директория {app_dir} не найдена")
        return
    
    # Находим все Python файлы
    for root, dirs, files in os.walk(app_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_imports_in_file(file_path)

def fix_imports_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Исправляем импорты py_commons
        content = re.sub(
            r'from py_commons\.',
            'from commons.',
            content
        )
        
        content = re.sub(
            r'import py_commons',
            'import commons',
            content
        )
        
        # Убираем sys.path.append строки
        content = re.sub(
            r'import sys\nsys\.path\.append\([\'"]/app/packages[\'"]\)\n',
            '',
            content
        )
        
        content = re.sub(
            r'sys\.path\.append\([\'"]/app/packages[\'"]\)\n',
            '',
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
        fix_imports_in_service(service)
    
    print("Все импорты исправлены!")
