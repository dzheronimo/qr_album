"""
Подключение к базе данных для Billing сервиса.

Содержит настройки подключения к PostgreSQL и создание сессий.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config import Settings
from app.models.billing import Base

settings = Settings()

# Создание асинхронного движка базы данных
engine = create_async_engine(
    settings.get_database_url(),
    echo=False,  # Установить True для отладки SQL запросов
    poolclass=NullPool,  # Отключаем пул соединений для разработки
    future=True
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncSession:
    """
    Получение сессии базы данных.
    
    Yields:
        AsyncSession: Сессия базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализация базы данных.
    
    Создает все таблицы в базе данных.
    """
    async with engine.begin() as conn:
        # Создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Закрытие соединения с базой данных.
    """
    await engine.dispose()
