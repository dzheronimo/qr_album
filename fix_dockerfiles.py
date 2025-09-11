#!/usr/bin/env python3
"""
Скрипт для исправления всех Dockerfile с правильными путями
"""

import os
import re

# Список всех Python сервисов
services = [
    'api-gateway',
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

def fix_dockerfile(service_name):
    dockerfile_path = f"apps/{service_name}/Dockerfile"
    
    if not os.path.exists(dockerfile_path):
        print(f"Файл {dockerfile_path} не найден")
        return
    
    with open(dockerfile_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем пути
    content = re.sub(
        r'COPY ../../packages/py-commons ./packages/py-commons',
        'COPY packages/py-commons ./packages/py-commons',
        content
    )
    
    content = re.sub(
        r'COPY requirements\.txt \.',
        f'COPY apps/{service_name}/requirements.txt .',
        content
    )
    
    content = re.sub(
        r'COPY app ./app',
        f'COPY apps/{service_name}/app ./app',
        content
    )
    
    with open(dockerfile_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Исправлен {dockerfile_path}")

if __name__ == "__main__":
    for service in services:
        fix_dockerfile(service)
    
    print("Все Dockerfile исправлены!")
