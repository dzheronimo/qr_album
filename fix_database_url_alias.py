#!/usr/bin/env python3
"""
Скрипт для добавления алиаса DATABASE_URL во все сервисы.
"""

import os
import re

def fix_database_url_alias():
    """Добавляет алиас DATABASE_URL во все сервисы."""
    
    # Список всех сервисов
    services = [
        "album-svc", "analytics-svc", "api-gateway", "auth-svc", 
        "billing-svc", "media-svc", "moderation-svc", "notification-svc", 
        "print-svc", "qr-svc", "scan-gateway", "user-profile-svc"
    ]
    
    for service in services:
        settings_file = f"apps/{service}/app/commons/settings.py"
        
        if not os.path.exists(settings_file):
            print(f"Файл {settings_file} не найден, пропускаем")
            continue
            
        print(f"Обновляем {settings_file}...")
        
        # Читаем файл
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем database_url поле на версию с алиасом
        pattern = r'database_url: str = Field\(default="", description="Полный URL для подключения к базе данных"\)'
        replacement = 'database_url: str = Field(default="", alias="DATABASE_URL", description="Полный URL для подключения к базе данных")'
        
        new_content = re.sub(pattern, replacement, content)
        
        # Записываем обновленный файл
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {settings_file} обновлен")

if __name__ == "__main__":
    fix_database_url_alias()
    print("🎉 Все файлы настроек обновлены!")


