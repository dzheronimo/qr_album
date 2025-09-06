#!/usr/bin/env python3
"""
Скрипт для исправления импортов health модуля во всех Python сервисах
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
        
        # Проверяем, есть ли импорт health
        if 'from health import' in content:
            print(f"Исправляю импорты в {file_path}")
            
            # Заменяем импорт health
            content = re.sub(
                r'from health import',
                'import sys\nsys.path.append(\'/app/packages/py-commons\')\nfrom health import',
                content
            )
            
            # Убираем дублирующиеся sys.path.append
            lines = content.split('\n')
            new_lines = []
            sys_path_added = False
            
            for line in lines:
                if 'sys.path.append(\'/app/packages/py-commons\')' in line:
                    if not sys_path_added:
                        new_lines.append(line)
                        sys_path_added = True
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ Исправлен {file_path}")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке {file_path}: {e}")

def main():
    print("Исправляю импорты health модуля во всех Python сервисах...")
    
    for service in services:
        print(f"\nОбрабатываю {service}...")
        fix_health_imports_in_service(service)
    
    print("\n✅ Все импорты исправлены!")

if __name__ == "__main__":
    main()
