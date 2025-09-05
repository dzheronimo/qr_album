"""
Middleware для rate limiting.

Ограничивает количество запросов от одного IP или пользователя.
"""

import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Settings

settings = Settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения скорости запросов."""
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
            requests_per_minute: Максимальное количество запросов в минуту
            requests_per_hour: Максимальное количество запросов в час
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests: Dict[str, list] = {}
        self.exclude_paths = [
            "/healthz",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с проверкой rate limiting.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Проверяем, нужно ли исключить путь из rate limiting
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Получаем идентификатор клиента
        client_id = self._get_client_id(request)
        
        # Проверяем rate limit
        if not self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Превышен лимит запросов",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Записываем запрос
        self._record_request(client_id)
        
        return await call_next(request)
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        Проверяет, нужно ли исключить путь из rate limiting.
        
        Args:
            path: Путь запроса
            
        Returns:
            bool: True если путь нужно исключить
        """
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    
    def _get_client_id(self, request: Request) -> str:
        """
        Получает идентификатор клиента для rate limiting.
        
        Args:
            request: HTTP запрос
            
        Returns:
            str: Идентификатор клиента
        """
        # Приоритет: user_id > IP адрес
        if hasattr(request.state, 'user_id') and request.state.user_id:
            return f"user:{request.state.user_id}"
        
        # Получаем IP адрес
        client_ip = request.client.host if request.client else "unknown"
        
        # Учитываем X-Forwarded-For для прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """
        Проверяет, не превышен ли rate limit для клиента.
        
        Args:
            client_id: Идентификатор клиента
            
        Returns:
            bool: True если запрос разрешен
        """
        current_time = time.time()
        
        # Получаем историю запросов для клиента
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        client_requests = self.requests[client_id]
        
        # Удаляем старые запросы (старше часа)
        client_requests[:] = [
            req_time for req_time in client_requests
            if current_time - req_time < 3600
        ]
        
        # Проверяем лимит в час
        if len(client_requests) >= self.requests_per_hour:
            return False
        
        # Проверяем лимит в минуту
        minute_ago = current_time - 60
        recent_requests = [
            req_time for req_time in client_requests
            if req_time > minute_ago
        ]
        
        if len(recent_requests) >= self.requests_per_minute:
            return False
        
        return True
    
    def _record_request(self, client_id: str) -> None:
        """
        Записывает запрос для клиента.
        
        Args:
            client_id: Идентификатор клиента
        """
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        self.requests[client_id].append(current_time)
        
        # Очищаем старые записи периодически
        if len(self.requests[client_id]) > self.requests_per_hour * 2:
            self.requests[client_id] = self.requests[client_id][-self.requests_per_hour:]


class AdvancedRateLimitMiddleware(BaseHTTPMiddleware):
    """Продвинутый middleware для rate limiting с разными лимитами для разных эндпоинтов."""
    
    def __init__(self, app):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
        """
        super().__init__(app)
        self.rate_limits = {
            "/auth/": {"requests_per_minute": 10, "requests_per_hour": 100},
            "/api/": {"requests_per_minute": 60, "requests_per_hour": 1000},
            "/scan/": {"requests_per_minute": 30, "requests_per_hour": 500},
            "default": {"requests_per_minute": 30, "requests_per_hour": 500},
        }
        self.requests: Dict[str, list] = {}
        self.exclude_paths = [
            "/healthz",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с проверкой rate limiting.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Проверяем, нужно ли исключить путь из rate limiting
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Получаем лимиты для пути
        rate_limit = self._get_rate_limit_for_path(request.url.path)
        
        # Получаем идентификатор клиента
        client_id = self._get_client_id(request)
        
        # Проверяем rate limit
        if not self._check_rate_limit(client_id, rate_limit):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Превышен лимит запросов",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Записываем запрос
        self._record_request(client_id)
        
        return await call_next(request)
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        Проверяет, нужно ли исключить путь из rate limiting.
        
        Args:
            path: Путь запроса
            
        Returns:
            bool: True если путь нужно исключить
        """
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    
    def _get_rate_limit_for_path(self, path: str) -> Dict[str, int]:
        """
        Получает лимиты для пути.
        
        Args:
            path: Путь запроса
            
        Returns:
            Dict[str, int]: Лимиты для пути
        """
        for prefix, limits in self.rate_limits.items():
            if path.startswith(prefix):
                return limits
        return self.rate_limits["default"]
    
    def _get_client_id(self, request: Request) -> str:
        """
        Получает идентификатор клиента для rate limiting.
        
        Args:
            request: HTTP запрос
            
        Returns:
            str: Идентификатор клиента
        """
        # Приоритет: user_id > IP адрес
        if hasattr(request.state, 'user_id') and request.state.user_id:
            return f"user:{request.state.user_id}"
        
        # Получаем IP адрес
        client_ip = request.client.host if request.client else "unknown"
        
        # Учитываем X-Forwarded-For для прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _check_rate_limit(self, client_id: str, rate_limit: Dict[str, int]) -> bool:
        """
        Проверяет, не превышен ли rate limit для клиента.
        
        Args:
            client_id: Идентификатор клиента
            rate_limit: Лимиты для проверки
            
        Returns:
            bool: True если запрос разрешен
        """
        current_time = time.time()
        
        # Получаем историю запросов для клиента
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        client_requests = self.requests[client_id]
        
        # Удаляем старые запросы (старше часа)
        client_requests[:] = [
            req_time for req_time in client_requests
            if current_time - req_time < 3600
        ]
        
        # Проверяем лимит в час
        if len(client_requests) >= rate_limit["requests_per_hour"]:
            return False
        
        # Проверяем лимит в минуту
        minute_ago = current_time - 60
        recent_requests = [
            req_time for req_time in client_requests
            if req_time > minute_ago
        ]
        
        if len(recent_requests) >= rate_limit["requests_per_minute"]:
            return False
        
        return True
    
    def _record_request(self, client_id: str) -> None:
        """
        Записывает запрос для клиента.
        
        Args:
            client_id: Идентификатор клиента
        """
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        self.requests[client_id].append(current_time)
        
        # Очищаем старые записи периодически
        if len(self.requests[client_id]) > 2000:  # Максимум 2000 записей на клиента
            self.requests[client_id] = self.requests[client_id][-1000:]
