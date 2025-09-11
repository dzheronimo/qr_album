"""
Общие health endpoints для микросервисов.

Содержит стандартные health и readiness проверки.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Awaitable
from enum import Enum

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Статусы здоровья сервиса."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class DependencyCheck(BaseModel):
    """Результат проверки зависимости."""
    name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Ответ health endpoint."""
    status: HealthStatus
    timestamp: datetime
    version: Optional[str] = None
    uptime_seconds: Optional[float] = None
    dependencies: Optional[List[DependencyCheck]] = None


class ReadinessResponse(BaseModel):
    """Ответ readiness endpoint."""
    status: HealthStatus
    timestamp: datetime
    ready: bool
    dependencies: List[DependencyCheck]


class HealthChecker:
    """Класс для проверки здоровья сервиса."""
    
    def __init__(self, service_name: str, version: Optional[str] = None):
        self.service_name = service_name
        self.version = version
        self.start_time = datetime.utcnow()
        self.dependency_checks: List[Callable[[], Awaitable[DependencyCheck]]] = []
    
    def add_dependency_check(self, check_func: Callable[[], Awaitable[DependencyCheck]]):
        """Добавляет проверку зависимости."""
        self.dependency_checks.append(check_func)
    
    def get_uptime(self) -> float:
        """Возвращает время работы сервиса в секундах."""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    async def check_dependencies(self) -> List[DependencyCheck]:
        """Проверяет все зависимости."""
        if not self.dependency_checks:
            return []
        
        # Выполняем проверки параллельно
        tasks = [check() for check in self.dependency_checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        dependency_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                dependency_results.append(DependencyCheck(
                    name=f"dependency_{i}",
                    status=HealthStatus.UNHEALTHY,
                    error=str(result)
                ))
            else:
                dependency_results.append(result)
        
        return dependency_results
    
    async def get_health_status(self) -> HealthResponse:
        """Возвращает статус здоровья сервиса."""
        dependencies = await self.check_dependencies()
        
        # Определяем общий статус
        if not dependencies:
            status = HealthStatus.HEALTHY
        else:
            unhealthy_count = sum(1 for dep in dependencies if dep.status == HealthStatus.UNHEALTHY)
            degraded_count = sum(1 for dep in dependencies if dep.status == HealthStatus.DEGRADED)
            
            if unhealthy_count > 0:
                status = HealthStatus.UNHEALTHY
            elif degraded_count > 0:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
        
        return HealthResponse(
            status=status,
            timestamp=datetime.utcnow(),
            version=self.version,
            uptime_seconds=self.get_uptime(),
            dependencies=dependencies
        )
    
    async def get_readiness_status(self) -> ReadinessResponse:
        """Возвращает статус готовности сервиса."""
        dependencies = await self.check_dependencies()
        
        # Сервис готов, если все критические зависимости работают
        critical_dependencies_healthy = all(
            dep.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
            for dep in dependencies
        )
        
        ready = critical_dependencies_healthy
        
        # Определяем общий статус
        if not dependencies:
            status = HealthStatus.HEALTHY
        else:
            unhealthy_count = sum(1 for dep in dependencies if dep.status == HealthStatus.UNHEALTHY)
            degraded_count = sum(1 for dep in dependencies if dep.status == HealthStatus.DEGRADED)
            
            if unhealthy_count > 0:
                status = HealthStatus.UNHEALTHY
            elif degraded_count > 0:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
        
        return ReadinessResponse(
            status=status,
            timestamp=datetime.utcnow(),
            ready=ready,
            dependencies=dependencies
        )


# Глобальный экземпляр health checker
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Получает глобальный экземпляр health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker("unknown-service")
    return _health_checker


def setup_health_checker(service_name: str, version: Optional[str] = None) -> HealthChecker:
    """Настраивает глобальный health checker."""
    global _health_checker
    _health_checker = HealthChecker(service_name, version)
    return _health_checker


def create_health_router(service_name: str, version: Optional[str] = None) -> APIRouter:
    """Создаёт router с health endpoints."""
    router = APIRouter()
    health_checker = setup_health_checker(service_name, version)
    
    @router.get("/health", response_model=HealthResponse, tags=["health"])
    async def health():
        """Liveness probe - проверяет, что сервис работает."""
        try:
            return await health_checker.get_health_status()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service is unhealthy"
            )
    
    @router.get("/health/ready", response_model=ReadinessResponse, tags=["health"])
    async def readiness():
        """Readiness probe - проверяет, что сервис готов принимать запросы."""
        try:
            readiness_status = await health_checker.get_readiness_status()
            
            if not readiness_status.ready:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service is not ready"
                )
            
            return readiness_status
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service is not ready"
            )
    
    return router


# Утилиты для создания проверок зависимостей

async def check_database(database_url: str, name: str = "database") -> DependencyCheck:
    """Проверяет подключение к базе данных."""
    import time
    start_time = time.time()
    
    try:
        # Импортируем здесь, чтобы избежать циклических импортов
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError
        
        # Создаём синхронный engine для проверки
        engine = create_engine(database_url.replace("+asyncpg", ""))
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        response_time = (time.time() - start_time) * 1000
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.HEALTHY,
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Database check failed: {e}")
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            error=str(e)
        )


async def check_redis(redis_url: str, name: str = "redis") -> DependencyCheck:
    """Проверяет подключение к Redis."""
    import time
    start_time = time.time()
    
    try:
        import redis.asyncio as redis
        
        client = redis.from_url(redis_url)
        await client.ping()
        await client.close()
        
        response_time = (time.time() - start_time) * 1000
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.HEALTHY,
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Redis check failed: {e}")
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            error=str(e)
        )


async def check_rabbitmq(rabbitmq_url: str, name: str = "rabbitmq") -> DependencyCheck:
    """Проверяет подключение к RabbitMQ."""
    import time
    start_time = time.time()
    
    try:
        import aio_pika
        
        connection = await aio_pika.connect_robust(rabbitmq_url)
        await connection.close()
        
        response_time = (time.time() - start_time) * 1000
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.HEALTHY,
            response_time_ms=response_time
        )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"RabbitMQ check failed: {e}")
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            error=str(e)
        )


async def check_http_service(service_url: str, name: str = "http_service") -> DependencyCheck:
    """Проверяет доступность HTTP сервиса."""
    import time
    start_time = time.time()
    
    try:
        from .http import get_http_client
        
        client = get_http_client()
        response = await client.get(f"{service_url}/health", timeout=3.0)
        
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            return DependencyCheck(
                name=name,
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time
            )
        else:
            return DependencyCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=f"HTTP {response.status_code}"
            )
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"HTTP service check failed: {e}")
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            error=str(e)
        )


async def check_smtp(host: str, port: int, name: str = "smtp") -> DependencyCheck:
    """Проверяет подключение к SMTP серверу."""
    import time
    import socket
    
    start_time = time.time()
    
    try:
        # Простая проверка TCP подключения
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)  # Таймаут 2 секунды
        result = sock.connect_ex((host, port))
        sock.close()
        
        response_time = (time.time() - start_time) * 1000
        
        if result == 0:
            return DependencyCheck(
                name=name,
                status=HealthStatus.HEALTHY,
                response_time_ms=response_time,
                details={"host": host, "port": port}
            )
        else:
            return DependencyCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=f"Connection failed to {host}:{port}"
            )
            
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"SMTP check failed: {e}")
        
        return DependencyCheck(
            name=name,
            status=HealthStatus.UNHEALTHY,
            response_time_ms=response_time,
            error=str(e)
        )
