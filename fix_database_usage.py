#!/usr/bin/env python3
"""
Скрипт для исправления использования database_url во всех сервисах.
"""

import os
import re

def fix_database_usage():
    """Исправляет использование database_url во всех сервисах."""
    
    # Список всех сервисов
    services = [
        "album-svc", "analytics-svc", "api-gateway", "auth-svc", 
        "billing-svc", "media-svc", "moderation-svc", "notification-svc", 
        "print-svc", "scan-gateway", "user-profile-svc"
    ]
    
    for service in services:
        # Проверяем разные возможные имена файлов
        possible_files = [
            f"apps/{service}/app/database.py",
            f"apps/{service}/app/db.py"
        ]
        
        for db_file in possible_files:
            if os.path.exists(db_file):
                print(f"Обновляем {db_file}...")
                
                # Читаем файл
                with open(db_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Заменяем settings.database_url на settings.get_database_url()
                new_content = content.replace(
                    'settings.database_url',
                    'settings.get_database_url()'
                )
                
                # Записываем обновленный файл
                with open(db_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ {db_file} обновлен")
                break
        else:
            print(f"❌ Файл базы данных не найден для {service}")

if __name__ == "__main__":
    fix_database_usage()
    print("🎉 Все файлы базы данных обновлены!")


