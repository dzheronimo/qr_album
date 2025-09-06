"""
Надёжный HTTP клиент с circuit breaker, retry и connection pooling.

Содержит обёртку над httpx.AsyncClient с паттернами отказоустойчивости.
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any, Union
from contextlib import asynccontextmanager

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Простой circuit breaker для HTTP клиента."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Проверяет, можно ли выполнить запрос."""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def on_success(self):
        """Вызывается при успешном запросе."""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        """Вызывается при неудачном запросе."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


class ReliableHTTPClient:
    """Надёжный HTTP клиент с circuit breaker и retry."""
    
    def __init__(
        self,
        timeout: float = 5.0,
        connect_timeout: float = 3.0,
        max_keepalive_connections: int = 100,
        max_connections: int = 200,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_multiplier: float = 2.0,
        retry_max_delay: float = 10.0
    ):
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_keepalive_connections = max_keepalive_connections
        self.max_connections = max_connections
        self.circuit_breaker = CircuitBreaker(failure_threshold, recovery_timeout)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_multiplier = retry_multiplier
        self.retry_max_delay = retry_max_delay
        
        # Создаём HTTP клиент с connection pooling
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=connect_timeout),
            limits=httpx.Limits(
                max_keepalive_connections=max_keepalive_connections,
                max_connections=max_connections
            )
        )
    
    async def close(self):
        """Закрывает HTTP клиент."""
        await self._client.aclose()
    
    @asynccontextmanager
    async def _get_client(self):
        """Контекстный менеджер для HTTP клиента."""
        try:
            yield self._client
        except Exception as e:
            logger.error(f"HTTP client error: {e}")
            raise
    
    def _should_retry(self, exception: Exception) -> bool:
        """Определяет, нужно ли повторить запрос."""
        if isinstance(exception, httpx.TimeoutException):
            return True
        if isinstance(exception, httpx.ConnectError):
            return True
        if isinstance(exception, httpx.RemoteProtocolError):
            return True
        if isinstance(exception, httpx.HTTPStatusError):
            # Повторяем только для 5xx ошибок
            return 500 <= exception.response.status_code < 600
        return False
    
    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """Выполняет запрос с retry логикой."""
        
        # Проверяем circuit breaker
        if not self.circuit_breaker.can_execute():
            raise httpx.RequestError("Circuit breaker is OPEN")
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self._get_client() as client:
                    response = await client.request(method, url, **kwargs)
                    
                    # Проверяем статус код
                    if 500 <= response.status_code < 600:
                        raise httpx.HTTPStatusError(
                            f"Server error: {response.status_code}",
                            request=response.request,
                            response=response
                        )
                    
                    # Успешный запрос
                    self.circuit_breaker.on_success()
                    return response
                    
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e):
                    self.circuit_breaker.on_failure()
                    raise
                
                if attempt < self.max_retries:
                    # Вычисляем задержку с экспоненциальным backoff
                    delay = min(
                        self.retry_delay * (self.retry_multiplier ** attempt),
                        self.retry_max_delay
                    )
                    
                    # Добавляем jitter
                    jitter = delay * 0.1 * (0.5 - asyncio.get_event_loop().time() % 1)
                    delay += jitter
                    
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}. "
                        f"Retrying in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {e}")
                    self.circuit_breaker.on_failure()
                    raise
        
        # Этот код не должен выполняться, но на всякий случай
        if last_exception:
            raise last_exception
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET запрос."""
        return await self._make_request_with_retry("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """POST запрос."""
        return await self._make_request_with_retry("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        """PUT запрос."""
        return await self._make_request_with_retry("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """DELETE запрос."""
        return await self._make_request_with_retry("DELETE", url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> httpx.Response:
        """PATCH запрос."""
        return await self._make_request_with_retry("PATCH", url, **kwargs)
    
    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Универсальный запрос."""
        return await self._make_request_with_retry(method, url, **kwargs)


# Глобальный экземпляр клиента
_http_client: Optional[ReliableHTTPClient] = None


def get_http_client() -> ReliableHTTPClient:
    """Получает глобальный экземпляр HTTP клиента."""
    global _http_client
    if _http_client is None:
        _http_client = ReliableHTTPClient()
    return _http_client


async def close_http_client():
    """Закрывает глобальный HTTP клиент."""
    global _http_client
    if _http_client is not None:
        await _http_client.close()
        _http_client = None


# Удобные функции для быстрого использования
async def get(url: str, **kwargs) -> httpx.Response:
    """GET запрос через глобальный клиент."""
    client = get_http_client()
    return await client.get(url, **kwargs)


async def post(url: str, **kwargs) -> httpx.Response:
    """POST запрос через глобальный клиент."""
    client = get_http_client()
    return await client.post(url, **kwargs)


async def put(url: str, **kwargs) -> httpx.Response:
    """PUT запрос через глобальный клиент."""
    client = get_http_client()
    return await client.put(url, **kwargs)


async def delete(url: str, **kwargs) -> httpx.Response:
    """DELETE запрос через глобальный клиент."""
    client = get_http_client()
    return await client.delete(url, **kwargs)


async def patch(url: str, **kwargs) -> httpx.Response:
    """PATCH запрос через глобальный клиент."""
    client = get_http_client()
    return await client.patch(url, **kwargs)
