"""
Общие фикстуры для тестов.

Содержит общие настройки и фикстуры для всех тестов.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from packages.py_commons.integration import (
    RabbitMQClient, RedisClient, CacheConfig, 
    HTTPClientManager, ServiceConfigs
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создание event loop для тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура для тестовой базы данных.
    
    Yields:
        AsyncSession: Сессия тестовой базы данных
    """
    # Создаем in-memory SQLite базу для тестов
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Создаем фабрику сессий
    TestSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with TestSessionLocal() as session:
        yield session
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_redis_client() -> AsyncGenerator[RedisClient, None]:
    """
    Фикстура для тестового Redis клиента.
    
    Yields:
        RedisClient: Тестовый Redis клиент
    """
    config = CacheConfig(
        host="localhost",
        port=6379,
        db=15,  # Используем отдельную БД для тестов
        decode_responses=True
    )
    
    client = RedisClient(config)
    
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()


@pytest_asyncio.fixture
async def test_rabbitmq_client() -> AsyncGenerator[RabbitMQClient, None]:
    """
    Фикстура для тестового RabbitMQ клиента.
    
    Yields:
        RabbitMQClient: Тестовый RabbitMQ клиент
    """
    client = RabbitMQClient(
        connection_url="amqp://guest:guest@localhost:5672/",
        service_name="test-service",
        max_retries=1,
        retry_delay=0.1
    )
    
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()


@pytest_asyncio.fixture
async def test_http_client_manager() -> AsyncGenerator[HTTPClientManager, None]:
    """
    Фикстура для тестового HTTP клиент менеджера.
    
    Yields:
        HTTPClientManager: Тестовый HTTP клиент менеджер
    """
    manager = HTTPClientManager()
    
    # Регистрируем тестовые сервисы
    manager.register_service(ServiceConfigs.auth_service("http://localhost:8001"))
    manager.register_service(ServiceConfigs.album_service("http://localhost:8002"))
    manager.register_service(ServiceConfigs.media_service("http://localhost:8003"))
    manager.register_service(ServiceConfigs.qr_service("http://localhost:8004"))
    
    try:
        yield manager
    finally:
        await manager.close_all()


@pytest.fixture
def test_user_data() -> dict:
    """Тестовые данные пользователя."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "is_active": True,
        "is_verified": True
    }


@pytest.fixture
def test_album_data() -> dict:
    """Тестовые данные альбома."""
    return {
        "id": 1,
        "title": "Test Album",
        "description": "Test album description",
        "user_id": 1,
        "is_public": True,
        "cover_image_url": "https://example.com/cover.jpg"
    }


@pytest.fixture
def test_page_data() -> dict:
    """Тестовые данные страницы."""
    return {
        "id": 1,
        "title": "Test Page",
        "content": "Test page content",
        "album_id": 1,
        "page_number": 1,
        "media_files": []
    }


@pytest.fixture
def test_qr_data() -> dict:
    """Тестовые данные QR кода."""
    return {
        "id": "test-qr-123",
        "url": "https://example.com/qr/test-qr-123",
        "page_id": 1,
        "album_id": 1,
        "user_id": 1,
        "scan_count": 0,
        "is_active": True
    }


@pytest.fixture
def test_media_data() -> dict:
    """Тестовые данные медиафайла."""
    return {
        "id": 1,
        "filename": "test-image.jpg",
        "file_path": "/uploads/test-image.jpg",
        "file_size": 1024000,
        "mime_type": "image/jpeg",
        "page_id": 1,
        "album_id": 1,
        "user_id": 1
    }


@pytest.fixture
def test_subscription_data() -> dict:
    """Тестовые данные подписки."""
    return {
        "id": 1,
        "user_id": 1,
        "plan_id": 1,
        "status": "active",
        "start_date": "2024-01-01T00:00:00Z",
        "end_date": "2024-12-31T23:59:59Z",
        "auto_renew": True
    }


@pytest.fixture
def test_notification_data() -> dict:
    """Тестовые данные уведомления."""
    return {
        "id": 1,
        "user_id": 1,
        "type": "email",
        "title": "Test Notification",
        "message": "This is a test notification",
        "status": "pending",
        "template_id": 1
    }


@pytest.fixture
def test_moderation_data() -> dict:
    """Тестовые данные модерации."""
    return {
        "id": 1,
        "content_type": "album",
        "content_id": 1,
        "user_id": 1,
        "status": "pending",
        "ai_analysis": {
            "confidence": 0.95,
            "categories": ["safe"],
            "flags": []
        }
    }


@pytest.fixture
def test_print_job_data() -> dict:
    """Тестовые данные задания печати."""
    return {
        "id": 1,
        "user_id": 1,
        "job_type": "qr_label",
        "content_data": {
            "title": "Test QR Label",
            "qr_code_url": "https://example.com/qr/test.jpg"
        },
        "print_format": "pdf",
        "status": "pending",
        "priority": 1
    }


# Маркеры для тестов
def pytest_configure(config):
    """Настройка маркеров pytest."""
    config.addinivalue_line("markers", "unit: Unit тесты")
    config.addinivalue_line("markers", "integration: Integration тесты")
    config.addinivalue_line("markers", "e2e: End-to-end тесты")
    config.addinivalue_line("markers", "slow: Медленные тесты")
    config.addinivalue_line("markers", "auth: Тесты аутентификации")
    config.addinivalue_line("markers", "album: Тесты альбомов")
    config.addinivalue_line("markers", "media: Тесты медиафайлов")
    config.addinivalue_line("markers", "qr: Тесты QR кодов")
    config.addinivalue_line("markers", "billing: Тесты биллинга")
    config.addinivalue_line("markers", "notification: Тесты уведомлений")
    config.addinivalue_line("markers", "moderation: Тесты модерации")
    config.addinivalue_line("markers", "print: Тесты печати")
    config.addinivalue_line("markers", "integration: Тесты интеграции")
