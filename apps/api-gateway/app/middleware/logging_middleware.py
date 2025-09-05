"""
Middleware для логирования запросов.

Логирует все HTTP запросы с детальной информацией.
"""

import time
import json
from typing import Dict, Any
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from app.config import Settings

settings = Settings()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов."""
    
    def __init__(self, app, exclude_paths: list = None):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
            exclude_paths: Список путей, исключенных из логирования
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/healthz",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с логированием.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Проверяем, нужно ли исключить путь из логирования
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Засекаем время начала обработки
        start_time = time.time()
        
        # Получаем информацию о запросе
        request_info = self._get_request_info(request)
        
        # Логируем входящий запрос
        logger.info(
            "Incoming request",
            **request_info
        )
        
        # Обрабатываем запрос
        response = await call_next(request)
        
        # Вычисляем время обработки
        process_time = time.time() - start_time
        
        # Получаем информацию об ответе
        response_info = self._get_response_info(response, process_time)
        
        # Логируем ответ
        log_level = "info"
        if response.status_code >= 400:
            log_level = "error"
        elif response.status_code >= 300:
            log_level = "warning"
        
        getattr(logger, log_level)(
            "Request completed",
            **request_info,
            **response_info
        )
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        Проверяет, нужно ли исключить путь из логирования.
        
        Args:
            path: Путь запроса
            
        Returns:
            bool: True если путь нужно исключить
        """
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    
    def _get_request_info(self, request: Request) -> Dict[str, Any]:
        """
        Получает информацию о запросе.
        
        Args:
            request: HTTP запрос
            
        Returns:
            Dict[str, Any]: Информация о запросе
        """
        # Получаем IP адрес
        client_ip = request.client.host if request.client else "unknown"
        
        # Учитываем X-Forwarded-For для прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Получаем User-Agent
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Получаем Referer
        referer = request.headers.get("Referer")
        
        # Получаем информацию о пользователе
        user_id = None
        if hasattr(request.state, 'user_id') and request.state.user_id:
            user_id = request.state.user_id
        
        return {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "referer": referer,
            "user_id": user_id,
            "content_type": request.headers.get("Content-Type"),
            "content_length": request.headers.get("Content-Length"),
        }
    
    def _get_response_info(self, response, process_time: float) -> Dict[str, Any]:
        """
        Получает информацию об ответе.
        
        Args:
            response: HTTP ответ
            process_time: Время обработки в секундах
            
        Returns:
            Dict[str, Any]: Информация об ответе
        """
        return {
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "response_size": response.headers.get("Content-Length", 0),
        }


class DetailedLoggingMiddleware(BaseHTTPMiddleware):
    """Детальный middleware для логирования с дополнительной информацией."""
    
    def __init__(self, app, exclude_paths: list = None):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
            exclude_paths: Список путей, исключенных из логирования
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/healthz",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с детальным логированием.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Проверяем, нужно ли исключить путь из логирования
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Засекаем время начала обработки
        start_time = time.time()
        
        # Получаем информацию о запросе
        request_info = self._get_detailed_request_info(request)
        
        # Логируем входящий запрос
        logger.info(
            "Incoming request",
            **request_info
        )
        
        # Обрабатываем запрос
        response = await call_next(request)
        
        # Вычисляем время обработки
        process_time = time.time() - start_time
        
        # Получаем информацию об ответе
        response_info = self._get_detailed_response_info(response, process_time)
        
        # Логируем ответ
        log_level = "info"
        if response.status_code >= 400:
            log_level = "error"
        elif response.status_code >= 300:
            log_level = "warning"
        
        getattr(logger, log_level)(
            "Request completed",
            **request_info,
            **response_info
        )
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        Проверяет, нужно ли исключить путь из логирования.
        
        Args:
            path: Путь запроса
            
        Returns:
            bool: True если путь нужно исключить
        """
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    
    def _get_detailed_request_info(self, request: Request) -> Dict[str, Any]:
        """
        Получает детальную информацию о запросе.
        
        Args:
            request: HTTP запрос
            
        Returns:
            Dict[str, Any]: Детальная информация о запросе
        """
        # Получаем IP адрес
        client_ip = request.client.host if request.client else "unknown"
        
        # Учитываем X-Forwarded-For для прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Получаем все заголовки
        headers = dict(request.headers)
        
        # Получаем информацию о пользователе
        user_id = None
        is_authenticated = False
        if hasattr(request.state, 'user_id') and request.state.user_id:
            user_id = request.state.user_id
            is_authenticated = True
        
        # Получаем тело запроса (только для POST/PUT/PATCH)
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Читаем тело запроса синхронно
                body_bytes = request._body
                if body_bytes:
                    # Пытаемся декодировать как JSON
                    try:
                        body = json.loads(body_bytes.decode())
                    except:
                        # Если не JSON, оставляем как строку
                        body = body_bytes.decode()[:1000]  # Ограничиваем размер
            except:
                body = "Error reading body"
        
        return {
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": client_ip,
            "user_agent": headers.get("User-Agent", "unknown"),
            "referer": headers.get("Referer"),
            "user_id": user_id,
            "is_authenticated": is_authenticated,
            "content_type": headers.get("Content-Type"),
            "content_length": headers.get("Content-Length"),
            "headers": {k: v for k, v in headers.items() if k.lower() not in ["authorization", "cookie"]},
            "body": body,
        }
    
    def _get_detailed_response_info(self, response, process_time: float) -> Dict[str, Any]:
        """
        Получает детальную информацию об ответе.
        
        Args:
            response: HTTP ответ
            process_time: Время обработки в секундах
            
        Returns:
            Dict[str, Any]: Детальная информация об ответе
        """
        return {
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "response_size": response.headers.get("Content-Length", 0),
            "response_headers": dict(response.headers),
        }
