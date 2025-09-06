"""
Middleware для аутентификации.

Проверяет JWT токены и добавляет информацию о пользователе в запрос.
"""

import httpx
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Settings

settings = Settings()


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware для аутентификации пользователей."""
    
    def __init__(self, app, exclude_paths: Optional[list] = None):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
            exclude_paths: Список путей, исключенных из проверки аутентификации
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/health/ready",
            "/healthz",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
            "/admin-api/v1/auth/login",
            "/admin-api/v1/auth/register",
            "/admin-api/v1/auth/refresh",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/scan/",  # Публичные сканирования
            "/api/services",  # Список сервисов
            "/api/services/",  # Проверка здоровья сервисов
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с проверкой аутентификации.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Проверяем, нужно ли исключить путь из проверки аутентификации
        if self._should_exclude_path(request.url.path):
            return await call_next(request)
        
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Токен аутентификации не предоставлен"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Проверяем токен через auth-svc
            user_info = await self._verify_token(token)
            if not user_info:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Недействительный токен аутентификации"}
                )
            
            # Добавляем информацию о пользователе в запрос
            request.state.user = user_info
            request.state.user_id = user_info.get("user_id")
            request.state.is_authenticated = True
            
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": f"Ошибка проверки токена: {str(e)}"}
            )
        
        return await call_next(request)
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        Проверяет, нужно ли исключить путь из проверки аутентификации.
        
        Args:
            path: Путь запроса
            
        Returns:
            bool: True если путь нужно исключить
        """
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    
    async def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Проверяет токен через auth-svc.
        
        Args:
            token: JWT токен
            
        Returns:
            Optional[Dict[str, Any]]: Информация о пользователе или None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.auth_service_url}/auth/verify",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception:
            return None


class OptionalAuthMiddleware(BaseHTTPMiddleware):
    """Middleware для опциональной аутентификации."""
    
    def __init__(self, app):
        """
        Инициализация middleware.
        
        Args:
            app: FastAPI приложение
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Обработка запроса с опциональной проверкой аутентификации.
        
        Args:
            request: HTTP запрос
            call_next: Следующий middleware/handler
            
        Returns:
            HTTP ответ
        """
        # Инициализируем состояние аутентификации
        request.state.user = None
        request.state.user_id = None
        request.state.is_authenticated = False
        
        # Получаем токен из заголовка Authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            try:
                # Проверяем токен через auth-svc
                user_info = await self._verify_token(token)
                if user_info:
                    request.state.user = user_info
                    request.state.user_id = user_info.get("user_id")
                    request.state.is_authenticated = True
                    
            except Exception:
                # Игнорируем ошибки аутентификации для опционального middleware
                pass
        
        return await call_next(request)
    
    async def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Проверяет токен через auth-svc.
        
        Args:
            token: JWT токен
            
        Returns:
            Optional[Dict[str, Any]]: Информация о пользователе или None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.auth_service_url}/auth/verify",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception:
            return None
