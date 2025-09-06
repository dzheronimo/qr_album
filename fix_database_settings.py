#!/usr/bin/env python3
"""
Скрипт для исправления настроек базы данных во всех сервисах.
"""

import os
import re

def fix_database_settings():
    """Исправляет настройки базы данных во всех сервисах."""
    
    # Список всех сервисов
    services = [
        "album-svc", "analytics-svc", "api-gateway", "auth-svc", 
        "billing-svc", "media-svc", "moderation-svc", "notification-svc", 
        "print-svc", "scan-gateway", "user-profile-svc"
    ]
    
    # Новый код для DatabaseSettings
    new_database_settings = '''class DatabaseSettings(CommonSettings):
    """
    Настройки для сервисов с базой данных.
    
    Расширяет CommonSettings добавлением настроек базы данных.
    """
    
    # Database name - должно быть переопределено в каждом сервисе
    db_name: str = Field(..., description="Имя базы данных для сервиса")
    
    # DATABASE_URL from environment (takes precedence over individual fields)
    database_url: str = Field(default="", description="Полный URL для подключения к базе данных")

    def get_database_url(self) -> str:
        """
        Получает URL для подключения к базе данных.
        
        Если задан DATABASE_URL, использует его, иначе формирует из отдельных полей.
        
        Returns:
            URL для подключения к PostgreSQL
        """
        if self.database_url:
            return self.database_url
        
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.db_name}"
        )'''
    
    for service in services:
        settings_file = f"apps/{service}/app/commons/settings.py"
        
        if not os.path.exists(settings_file):
            print(f"Файл {settings_file} не найден, пропускаем")
            continue
            
        print(f"Обновляем {settings_file}...")
        
        # Читаем файл
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем старый DatabaseSettings на новый
        pattern = r'class DatabaseSettings\(CommonSettings\):.*?(?=\n\n|\nclass|\n\Z)'
        new_content = re.sub(pattern, new_database_settings, content, flags=re.DOTALL)
        
        # Записываем обновленный файл
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ {settings_file} обновлен")

if __name__ == "__main__":
    fix_database_settings()
    print("🎉 Все файлы настроек обновлены!")


