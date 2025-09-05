"""
HTTP клиент для межсервисного взаимодействия.

Содержит утилиты для HTTP запросов между сервисами.
"""

import asyncio
import logging
from typing import Any, Dict, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Конфигурация сервиса."""
    name: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    headers: Optional[Dict[str, str]] = None


@dataclass
class RequestConfig:
    """Конфигурация запроса."""
    timeout: Optional[int] = None
    max_retries: Optional[int] = None
    retry_delay: Optional[float] = None
    headers: Optional[Dict[str, str]] = None
    auth_token: Optional[str] = None


class ServiceHTTPClient:
    """HTTP клиент для взаимодействия с сервисами."""
    
    def __init__(self, service_config: ServiceConfig):
        """
        Инициализация клиента.
        
        Args:
            service_config: Конфигурация сервиса
        """
        self.config = service_config
        self.session: Optional[ClientSession] = None
        self._request_count = 0
        self._error_count = 0
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        await self.close()
    
    async def _create_session(self) -> None:
        """Создание HTTP сессии."""
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(total=self.config.timeout)
            self.session = ClientSession(
                base_url=self.config.base_url,
                timeout=timeout,
                headers=self.config.headers or {}
            )
    
    async def close(self) -> None:
        """Закрытие HTTP сессии."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        url: str,
        config: Optional[RequestConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Выполнение HTTP запроса с повторными попытками.
        
        Args:
            method: HTTP метод
            url: URL запроса
            config: Конфигурация запроса
            **kwargs: Дополнительные параметры запроса
            
        Returns:
            Dict[str, Any]: Ответ сервера
            
        Raises:
            ClientError: Ошибка HTTP клиента
        """
        await self._create_session()
        
        config = config or RequestConfig()
        max_retries = config.max_retries or self.config.max_retries
        retry_delay = config.retry_delay or self.config.retry_delay
        
        # Подготавливаем заголовки
        headers = kwargs.get('headers', {})
        if config.headers:
            headers.update(config.headers)
        if config.auth_token:
            headers['Authorization'] = f'Bearer {config.auth_token}'
        
        kwargs['headers'] = headers
        
        # Выполняем запрос с повторными попытками
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                self._request_count += 1
                
                async with self.session.request(method, url, **kwargs) as response:
                    if response.status < 400:
                        data = await response.json()
                        return {
                            "status": response.status,
                            "data": data,
                            "headers": dict(response.headers)
                        }
                    else:
                        error_data = await response.text()
                        raise ClientError(
                            f"HTTP {response.status}: {error_data}"
                        )
                        
            except Exception as e:
                last_error = e
                self._error_count += 1
                
                if attempt < max_retries:
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                else:
                    logger.error(f"Request failed after {max_retries + 1} attempts: {e}")
                    raise last_error
        
        raise last_error
    
    async def get(
        self,
        url: str,
        config: Optional[RequestConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """GET запрос."""
        return await self._make_request("GET", url, config, **kwargs)
    
    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        config: Optional[RequestConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """POST запрос."""
        if data:
            kwargs['json'] = data
        return await self._make_request("POST", url, config, **kwargs)
    
    async def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        config: Optional[RequestConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """PUT запрос."""
        if data:
            kwargs['json'] = data
        return await self._make_request("PUT", url, config, **kwargs)
    
    async def patch(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        config: Optional[RequestConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """PATCH запрос."""
        if data:
            kwargs['json'] = data
        return await self._make_request("PATCH", url, config, **kwargs)
    
    async def delete(
        self,
        url: str,
        config: Optional[RequestConfig] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """DELETE запрос."""
        return await self._make_request("DELETE", url, config, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики клиента."""
        return {
            "service_name": self.config.name,
            "base_url": self.config.base_url,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1)
        }


class HTTPClientManager:
    """Менеджер HTTP клиентов для всех сервисов."""
    
    def __init__(self):
        """Инициализация менеджера."""
        self.clients: Dict[str, ServiceHTTPClient] = {}
        self.configs: Dict[str, ServiceConfig] = {}
    
    def register_service(self, config: ServiceConfig) -> None:
        """
        Регистрация сервиса.
        
        Args:
            config: Конфигурация сервиса
        """
        self.configs[config.name] = config
        self.clients[config.name] = ServiceHTTPClient(config)
        logger.info(f"Registered service: {config.name}")
    
    def get_client(self, service_name: str) -> ServiceHTTPClient:
        """
        Получение клиента для сервиса.
        
        Args:
            service_name: Название сервиса
            
        Returns:
            ServiceHTTPClient: HTTP клиент
            
        Raises:
            KeyError: Сервис не найден
        """
        if service_name not in self.clients:
            raise KeyError(f"Service {service_name} not registered")
        
        return self.clients[service_name]
    
    async def close_all(self) -> None:
        """Закрытие всех клиентов."""
        for client in self.clients.values():
            await client.close()
        logger.info("Closed all HTTP clients")
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Получение статистики всех клиентов."""
        return {
            service_name: client.get_stats()
            for service_name, client in self.clients.items()
        }


# Предопределенные конфигурации сервисов
class ServiceConfigs:
    """Конфигурации сервисов по умолчанию."""
    
    @staticmethod
    def auth_service(base_url: str = "http://localhost:8001") -> ServiceConfig:
        """Конфигурация сервиса аутентификации."""
        return ServiceConfig(
            name="auth-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def album_service(base_url: str = "http://localhost:8002") -> ServiceConfig:
        """Конфигурация сервиса альбомов."""
        return ServiceConfig(
            name="album-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def media_service(base_url: str = "http://localhost:8003") -> ServiceConfig:
        """Конфигурация сервиса медиа."""
        return ServiceConfig(
            name="media-svc",
            base_url=base_url,
            timeout=60,  # Больше времени для загрузки файлов
            max_retries=3
        )
    
    @staticmethod
    def qr_service(base_url: str = "http://localhost:8004") -> ServiceConfig:
        """Конфигурация сервиса QR кодов."""
        return ServiceConfig(
            name="qr-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def user_profile_service(base_url: str = "http://localhost:8005") -> ServiceConfig:
        """Конфигурация сервиса профилей пользователей."""
        return ServiceConfig(
            name="user-profile-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def analytics_service(base_url: str = "http://localhost:8006") -> ServiceConfig:
        """Конфигурация сервиса аналитики."""
        return ServiceConfig(
            name="analytics-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def api_gateway(base_url: str = "http://localhost:8000") -> ServiceConfig:
        """Конфигурация API Gateway."""
        return ServiceConfig(
            name="api-gateway",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def billing_service(base_url: str = "http://localhost:8007") -> ServiceConfig:
        """Конфигурация сервиса биллинга."""
        return ServiceConfig(
            name="billing-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def notification_service(base_url: str = "http://localhost:8008") -> ServiceConfig:
        """Конфигурация сервиса уведомлений."""
        return ServiceConfig(
            name="notification-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def moderation_service(base_url: str = "http://localhost:8009") -> ServiceConfig:
        """Конфигурация сервиса модерации."""
        return ServiceConfig(
            name="moderation-svc",
            base_url=base_url,
            timeout=30,
            max_retries=3
        )
    
    @staticmethod
    def print_service(base_url: str = "http://localhost:8011") -> ServiceConfig:
        """Конфигурация сервиса печати."""
        return ServiceConfig(
            name="print-svc",
            base_url=base_url,
            timeout=60,  # Больше времени для генерации PDF
            max_retries=3
        )


# Утилиты для работы с токенами
class TokenManager:
    """Менеджер токенов для межсервисного взаимодействия."""
    
    def __init__(self, auth_client: ServiceHTTPClient):
        """
        Инициализация менеджера токенов.
        
        Args:
            auth_client: HTTP клиент сервиса аутентификации
        """
        self.auth_client = auth_client
        self._cached_tokens: Dict[str, Dict[str, Any]] = {}
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Валидация токена.
        
        Args:
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Данные пользователя
        """
        try:
            response = await self.auth_client.get(
                "/api/v1/auth/validate",
                config=RequestConfig(auth_token=token)
            )
            return response["data"]
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise
    
    async def get_user_info(self, user_id: int, token: str) -> Dict[str, Any]:
        """
        Получение информации о пользователе.
        
        Args:
            user_id: ID пользователя
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Информация о пользователе
        """
        try:
            response = await self.auth_client.get(
                f"/api/v1/users/{user_id}",
                config=RequestConfig(auth_token=token)
            )
            return response["data"]
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise
