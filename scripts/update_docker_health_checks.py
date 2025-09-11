#!/usr/bin/env python3
"""
Скрипт для добавления health checks и resource limits в docker-compose.yml.
"""

import re
from pathlib import Path

def update_docker_compose():
    """Обновляет docker-compose.yml с health checks и resource limits."""
    
    compose_file = Path("docker-compose.yml")
    
    # Читаем файл
    with open(compose_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Список микросервисов для обновления
    services = [
        "auth-svc", "album-svc", "media-svc", "qr-svc", "user-profile-svc",
        "analytics-svc", "billing-svc", "notification-svc", "moderation-svc",
        "print-svc", "scan-gateway"
    ]
    
    # Шаблон для добавления health checks и resource limits
    health_and_resources = '''
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    ulimits:
      nofile:
        soft: 65536
        hard: 65536'''
    
    # Обновляем каждый сервис
    for service in services:
        # Паттерн для поиска секции сервиса
        pattern = rf'(  # {service.replace("-", " ").title()} Service\n  {service}:.*?)(\n    networks:\n      - storyqr-network)'
        
        def replace_service(match):
            service_content = match.group(1)
            networks_section = match.group(2)
            
            # Проверяем, есть ли уже healthcheck
            if "healthcheck:" in service_content:
                return match.group(0)  # Не изменяем, если уже есть
            
            # Добавляем health checks и resource limits перед networks
            return service_content + health_and_resources + networks_section
        
        content = re.sub(pattern, replace_service, content, flags=re.DOTALL)
    
    # Записываем обновлённый файл
    with open(compose_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Updated docker-compose.yml with health checks and resource limits")

if __name__ == "__main__":
    update_docker_compose()
