#!/usr/bin/env python3
"""
Скрипт для массового обновления requirements.txt с безопасными зависимостями.
"""

import os
from pathlib import Path

def update_requirements(service_path: str):
    """Обновляет requirements.txt для сервиса."""
    requirements_path = Path(service_path) / "requirements.txt"
    
    if not requirements_path.exists():
        print(f"requirements.txt not found for {service_path}")
        return
    
    # Читаем текущий файл
    with open(requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, уже ли обновлён
    if "setuptools>=78.1.1" in content:
        print(f"requirements.txt already updated for {service_path}")
        return
    
    # Добавляем безопасные зависимости
    new_dependencies = [
        "setuptools>=78.1.1",
        "redis>=5.0.0", 
        "aio-pika>=9.0.0",
        "tenacity>=8.0.0"
    ]
    
    # Добавляем зависимости в конец файла
    content = content.rstrip() + "\n" + "\n".join(new_dependencies) + "\n"
    
    # Записываем обновлённый файл
    with open(requirements_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated requirements.txt for {service_path}")

def main():
    """Основная функция."""
    print("Updating requirements.txt for all services...")
    
    # Список сервисов
    services = [
        "apps/api-gateway",
        "apps/album-svc", 
        "apps/analytics-svc",
        "apps/billing-svc",
        "apps/media-svc",
        "apps/moderation-svc",
        "apps/notification-svc",
        "apps/print-svc",
        "apps/qr-svc",
        "apps/scan-gateway",
        "apps/user-profile-svc"
    ]
    
    for service in services:
        try:
            update_requirements(service)
        except Exception as e:
            print(f"Error updating {service}: {e}")
    
    print("Requirements update completed!")

if __name__ == "__main__":
    main()
