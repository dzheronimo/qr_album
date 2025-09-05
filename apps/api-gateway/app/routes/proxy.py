"""
Роуты для проксирования запросов к микросервисам.
"""

import httpx
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from loguru import logger

from app.config import Settings

settings = Settings()
router = APIRouter()


class ServiceProxy:
    """Прокси для маршрутизации запросов к микросервисам."""
    
    def __init__(self):
        """Инициализация прокси."""
        self.service_urls = {
            "auth": settings.auth_service_url,
            "user-profile": settings.user_profile_service_url,
            "album": settings.album_service_url,
            "media": settings.media_service_url,
            "qr": settings.qr_service_url,
            "analytics": settings.analytics_service_url,
            "billing": settings.billing_service_url,
            "notification": settings.notification_service_url,
            "moderation": settings.moderation_service_url,
            "print": settings.print_service_url,
        }
    
    async def proxy_request(
        self,
        service_name: str,
        path: str,
        request: Request,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> StreamingResponse:
        """
        Проксирует запрос к микросервису.
        
        Args:
            service_name: Имя сервиса
            path: Путь в сервисе
            request: Исходный запрос
            method: HTTP метод
            data: Данные для отправки
            params: Параметры запроса
            headers: Дополнительные заголовки
            
        Returns:
            StreamingResponse: Ответ от микросервиса
        """
        if service_name not in self.service_urls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Сервис {service_name} не найден"
            )
        
        service_url = self.service_urls[service_name]
        target_url = f"{service_url}{path}"
        
        # Подготавливаем заголовки
        proxy_headers = self._prepare_headers(request, headers)
        
        # Подготавливаем параметры
        query_params = self._prepare_params(request, params)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Выполняем запрос к микросервису
                response = await client.request(
                    method=method,
                    url=target_url,
                    headers=proxy_headers,
                    params=query_params,
                    json=data if data else None,
                    content=await request.body() if method in ["POST", "PUT", "PATCH"] else None,
                    follow_redirects=True
                )
                
                # Логируем запрос
                logger.info(
                    f"Proxied request to {service_name}",
                    method=method,
                    url=target_url,
                    status_code=response.status_code,
                    user_id=getattr(request.state, 'user_id', None)
                )
                
                # Возвращаем ответ как поток
                return StreamingResponse(
                    self._stream_response(response),
                    status_code=response.status_code,
                    headers=self._filter_headers(response.headers),
                    media_type=response.headers.get("content-type")
                )
                
        except httpx.TimeoutException:
            logger.error(f"Timeout when proxying to {service_name}: {target_url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Таймаут при обращении к сервису"
            )
        except httpx.ConnectError:
            logger.error(f"Connection error when proxying to {service_name}: {target_url}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Сервис недоступен"
            )
        except Exception as e:
            logger.error(f"Error when proxying to {service_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при обращении к сервису"
            )
    
    def _prepare_headers(self, request: Request, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Подготавливает заголовки для проксирования.
        
        Args:
            request: Исходный запрос
            additional_headers: Дополнительные заголовки
            
        Returns:
            Dict[str, str]: Заголовки для проксирования
        """
        headers = {}
        
        # Копируем важные заголовки
        important_headers = [
            "Authorization",
            "Content-Type",
            "Accept",
            "User-Agent",
            "X-Forwarded-For",
            "X-Real-IP",
        ]
        
        for header in important_headers:
            if header in request.headers:
                headers[header] = request.headers[header]
        
        # Добавляем информацию о пользователе
        if hasattr(request.state, 'user_id') and request.state.user_id:
            headers["X-User-ID"] = str(request.state.user_id)
        
        if hasattr(request.state, 'is_authenticated') and request.state.is_authenticated:
            headers["X-Authenticated"] = "true"
        
        # Добавляем дополнительные заголовки
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _prepare_params(self, request: Request, additional_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Подготавливает параметры для проксирования.
        
        Args:
            request: Исходный запрос
            additional_params: Дополнительные параметры
            
        Returns:
            Dict[str, Any]: Параметры для проксирования
        """
        params = dict(request.query_params)
        
        # Добавляем дополнительные параметры
        if additional_params:
            params.update(additional_params)
        
        return params
    
    def _filter_headers(self, response_headers: httpx.Headers) -> Dict[str, str]:
        """
        Фильтрует заголовки ответа.
        
        Args:
            response_headers: Заголовки ответа от микросервиса
            
        Returns:
            Dict[str, str]: Отфильтрованные заголовки
        """
        # Заголовки, которые нужно исключить
        exclude_headers = {
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
            "server",
        }
        
        filtered_headers = {}
        for key, value in response_headers.items():
            if key.lower() not in exclude_headers:
                filtered_headers[key] = value
        
        return filtered_headers
    
    async def _stream_response(self, response: httpx.Response):
        """
        Потоково возвращает ответ от микросервиса.
        
        Args:
            response: Ответ от микросервиса
            
        Yields:
            bytes: Чанки данных
        """
        async for chunk in response.aiter_bytes():
            yield chunk


# Создаем экземпляр прокси
service_proxy = ServiceProxy()


@router.api_route("/api/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_service(
    service_name: str,
    path: str,
    request: Request
):
    """
    Проксирует запросы к микросервисам.
    
    Args:
        service_name: Имя сервиса
        path: Путь в сервисе
        request: HTTP запрос
        
    Returns:
        StreamingResponse: Ответ от микросервиса
    """
    return await service_proxy.proxy_request(
        service_name=service_name,
        path=f"/{path}" if not path.startswith("/") else path,
        request=request,
        method=request.method
    )


@router.get("/api/services")
async def list_services():
    """
    Возвращает список доступных сервисов.
    
    Returns:
        Dict[str, str]: Список сервисов и их URL
    """
    return {
        "services": service_proxy.service_urls,
        "total": len(service_proxy.service_urls)
    }


@router.get("/api/services/{service_name}/health")
async def check_service_health(service_name: str):
    """
    Проверяет здоровье сервиса.
    
    Args:
        service_name: Имя сервиса
        
    Returns:
        Dict[str, Any]: Статус здоровья сервиса
    """
    if service_name not in service_proxy.service_urls:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Сервис {service_name} не найден"
        )
    
    service_url = service_proxy.service_urls[service_name]
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{service_url}/healthz")
            
            return {
                "service": service_name,
                "url": service_url,
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds()
            }
            
    except Exception as e:
        return {
            "service": service_name,
            "url": service_url,
            "status": "unhealthy",
            "error": str(e)
        }
