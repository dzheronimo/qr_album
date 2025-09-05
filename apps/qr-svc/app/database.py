"""
Настройка подключения к базе данных для QR сервиса.

Содержит конфигурацию SQLAlchemy для работы с базой данных.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.models import Base

settings = Settings()

# Создание асинхронного движка базы данных
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Установить True для отладки SQL запросов
    future=True,
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency для получения сессии базы данных.
    
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
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Закрытие соединений с базой данных.
    """
    await engine.dispose()
