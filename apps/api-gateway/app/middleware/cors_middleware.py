"""
Middleware для CORS.

Настраивает Cross-Origin Resource Sharing для API Gateway.
"""

from typing import List, Optional
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import Settings

settings = Settings()


class CORSMiddleware(BaseHTTPMiddleware):
    """Кастомный middleware для CORS."""
    
    def __init__(
        self,
        app,
        allow_origins: Optional[List[str]] = None,
        allow_credentials: bool = True,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
        expose_headers: Optional[List[str]] = None,
        max_age: int = 600,
    ):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
            allow_origins: Разрешенные источники
            allow_credentials: Разрешить credentials
            allow_methods: Разрешенные HTTP методы
            allow_headers: Разрешенные заголовки
            expose_headers: Заголовки для экспозиции
            max_age: Максимальное время кэширования preflight запросов
        """
        super().__init__(app)
        
        self.allow_origins = allow_origins or ["*"]
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allow_headers = allow_headers or [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRFToken",
            "X-API-Key",
        ]
        self.expose_headers = expose_headers or [
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page",
        ]
        self.max_age = max_age
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с CORS заголовками.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Получаем origin из запроса
        origin = request.headers.get("Origin")
        
        # Проверяем, разрешен ли origin
        if self._is_origin_allowed(origin):
            # Обрабатываем preflight запрос
            if request.method == "OPTIONS":
                response = Response()
                self._add_cors_headers(response, origin)
                return response
            
            # Обрабатываем обычный запрос
            response = await call_next(request)
            self._add_cors_headers(response, origin)
            return response
        else:
            # Origin не разрешен
            if request.method == "OPTIONS":
                response = Response(status_code=403)
                return response
            
            # Обрабатываем обычный запрос без CORS заголовков
            return await call_next(request)
    
    def _is_origin_allowed(self, origin: Optional[str]) -> bool:
        """
        Проверяет, разрешен ли origin.
        
        Args:
            origin: Origin из заголовка запроса
            
        Returns:
            bool: True если origin разрешен
        """
        if not origin:
            return True  # Разрешаем запросы без origin (например, из Postman)
        
        if "*" in self.allow_origins:
            return True
        
        return origin in self.allow_origins
    
    def _add_cors_headers(self, response: Response, origin: Optional[str]) -> None:
        """
        Добавляет CORS заголовки к ответу.
        
        Args:
            response: HTTP ответ
            origin: Origin из заголовка запроса
        """
        if origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.allow_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        response.headers["Access-Control-Max-Age"] = str(self.max_age)


class DevelopmentCORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware для разработки (более мягкие настройки)."""
    
    def __init__(self, app):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с CORS заголовками для разработки.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Обрабатываем preflight запрос
        if request.method == "OPTIONS":
            response = Response()
            self._add_development_cors_headers(response)
            return response
        
        # Обрабатываем обычный запрос
        response = await call_next(request)
        self._add_development_cors_headers(response)
        return response
    
    def _add_development_cors_headers(self, response: Response) -> None:
        """
        Добавляет CORS заголовки для разработки.
        
        Args:
            response: HTTP ответ
        """
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = (
            "Accept, Accept-Language, Content-Language, Content-Type, "
            "Authorization, X-Requested-With, X-CSRFToken, X-API-Key"
        )
        response.headers["Access-Control-Expose-Headers"] = (
            "X-Total-Count, X-Page-Count, X-Current-Page"
        )
        response.headers["Access-Control-Max-Age"] = "600"


class ProductionCORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware для продакшена (строгие настройки)."""
    
    def __init__(self, app, allowed_origins: List[str]):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
            allowed_origins: Список разрешенных origins
        """
        super().__init__(app)
        self.allowed_origins = allowed_origins
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с CORS заголовками для продакшена.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        origin = request.headers.get("Origin")
        
        # Проверяем, разрешен ли origin
        if origin and origin in self.allowed_origins:
            # Обрабатываем preflight запрос
            if request.method == "OPTIONS":
                response = Response()
                self._add_production_cors_headers(response, origin)
                return response
            
            # Обрабатываем обычный запрос
            response = await call_next(request)
            self._add_production_cors_headers(response, origin)
            return response
        else:
            # Origin не разрешен
            if request.method == "OPTIONS":
                response = Response(status_code=403)
                return response
            
            # Обрабатываем обычный запрос без CORS заголовков
            return await call_next(request)
    
    def _add_production_cors_headers(self, response: Response, origin: str) -> None:
        """
        Добавляет CORS заголовки для продакшена.
        
        Args:
            response: HTTP ответ
            origin: Разрешенный origin
        """
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = (
            "Accept, Accept-Language, Content-Language, Content-Type, "
            "Authorization, X-Requested-With, X-CSRFToken, X-API-Key"
        )
        response.headers["Access-Control-Expose-Headers"] = (
            "X-Total-Count, X-Page-Count, X-Current-Page"
        )
        response.headers["Access-Control-Max-Age"] = "600"
