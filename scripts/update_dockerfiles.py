#!/usr/bin/env python3
"""
Скрипт для массового обновления Dockerfile с non-root пользователями и health checks.
"""

import os
from pathlib import Path

def update_dockerfile(service_path: str):
    """Обновляет Dockerfile для сервиса."""
    dockerfile_path = Path(service_path) / "Dockerfile"
    
    if not dockerfile_path.exists():
        print(f"Dockerfile not found for {service_path}")
        return
    
    # Читаем текущий Dockerfile
    with open(dockerfile_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем, уже ли обновлён
    if "USER appuser" in content:
        print(f"Dockerfile already updated for {service_path}")
        return
    
    # Создаём новый контент
    new_content = '''FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Создаём non-root пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app ./app

# Устанавливаем права на директорию
RUN chown -R appuser:appuser /app

# Переключаемся на non-root пользователя
USER appuser

ENV PYTHONUNBUFFERED=1

# Добавляем health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    # Записываем новый файл
    with open(dockerfile_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated Dockerfile for {service_path}")

def main():
    """Основная функция."""
    print("Updating Dockerfiles for all services...")
    
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
            update_dockerfile(service)
        except Exception as e:
            print(f"Error updating {service}: {e}")
    
    print("Dockerfiles update completed!")

if __name__ == "__main__":
    main()
