"""
HTTP клиенты для взаимодействия с другими сервисами.

Содержит настройки и утилиты для HTTP запросов к другим сервисам.
"""

import logging
from typing import Dict, Any, Optional

from packages.py_commons.integration import (
    HTTPClientManager, ServiceConfigs, ServiceHTTPClient, 
    RequestConfig, TokenManager
)

logger = logging.getLogger(__name__)


class ServiceClients:
    """HTTP клиенты для взаимодействия с другими сервисами."""
    
    def __init__(self):
        """Инициализация клиентов сервисов."""
        self.client_manager = HTTPClientManager()
        self.token_manager: Optional[TokenManager] = None
        self._setup_clients()
    
    def _setup_clients(self) -> None:
        """Настройка клиентов сервисов."""
        # Регистрируем все сервисы
        self.client_manager.register_service(ServiceConfigs.album_service())
        self.client_manager.register_service(ServiceConfigs.media_service())
        self.client_manager.register_service(ServiceConfigs.qr_service())
        self.client_manager.register_service(ServiceConfigs.user_profile_service())
        self.client_manager.register_service(ServiceConfigs.analytics_service())
        self.client_manager.register_service(ServiceConfigs.billing_service())
        self.client_manager.register_service(ServiceConfigs.notification_service())
        self.client_manager.register_service(ServiceConfigs.moderation_service())
        self.client_manager.register_service(ServiceConfigs.print_service())
        
        # Настраиваем менеджер токенов
        auth_client = self.client_manager.get_client("auth-svc")
        self.token_manager = TokenManager(auth_client)
        
        logger.info("Service clients initialized")
    
    async def close_all(self) -> None:
        """Закрытие всех клиентов."""
        await self.client_manager.close_all()
        logger.info("All service clients closed")
    
    def get_client(self, service_name: str) -> ServiceHTTPClient:
        """
        Получение клиента для сервиса.
        
        Args:
            service_name: Название сервиса
            
        Returns:
            ServiceHTTPClient: HTTP клиент
        """
        return self.client_manager.get_client(service_name)
    
    async def validate_user_token(self, token: str) -> Dict[str, Any]:
        """
        Валидация токена пользователя.
        
        Args:
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Данные пользователя
        """
        if not self.token_manager:
            raise ValueError("Token manager not initialized")
        
        return await self.token_manager.validate_token(token)
    
    async def get_user_profile(self, user_id: int, token: str) -> Dict[str, Any]:
        """
        Получение профиля пользователя.
        
        Args:
            user_id: ID пользователя
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Профиль пользователя
        """
        client = self.get_client("user-profile-svc")
        
        response = await client.get(
            f"/api/v1/profiles/{user_id}",
            config=RequestConfig(auth_token=token)
        )
        
        return response["data"]
    
    async def get_user_subscription(self, user_id: int, token: str) -> Dict[str, Any]:
        """
        Получение подписки пользователя.
        
        Args:
            user_id: ID пользователя
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Подписка пользователя
        """
        client = self.get_client("billing-svc")
        
        response = await client.get(
            f"/api/v1/subscriptions/user/{user_id}",
            config=RequestConfig(auth_token=token)
        )
        
        return response["data"]
    
    async def check_user_limits(self, user_id: int, token: str) -> Dict[str, Any]:
        """
        Проверка лимитов пользователя.
        
        Args:
            user_id: ID пользователя
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Информация о лимитах
        """
        client = self.get_client("billing-svc")
        
        response = await client.get(
            f"/api/v1/limits/user/{user_id}",
            config=RequestConfig(auth_token=token)
        )
        
        return response["data"]
    
    async def send_notification(
        self,
        user_id: int,
        notification_type: str,
        data: Dict[str, Any],
        token: str
    ) -> Dict[str, Any]:
        """
        Отправка уведомления пользователю.
        
        Args:
            user_id: ID пользователя
            notification_type: Тип уведомления
            data: Данные уведомления
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Результат отправки
        """
        client = self.get_client("notification-svc")
        
        response = await client.post(
            "/api/v1/notifications/send",
            data={
                "user_id": user_id,
                "notification_type": notification_type,
                "data": data
            },
            config=RequestConfig(auth_token=token)
        )
        
        return response["data"]
    
    async def log_analytics_event(
        self,
        user_id: int,
        event_type: str,
        data: Dict[str, Any],
        token: str
    ) -> None:
        """
        Логирование события аналитики.
        
        Args:
            user_id: ID пользователя
            event_type: Тип события
            data: Данные события
            token: JWT токен
        """
        client = self.get_client("analytics-svc")
        
        await client.post(
            "/api/v1/analytics/events",
            data={
                "user_id": user_id,
                "event_type": event_type,
                "data": data
            },
            config=RequestConfig(auth_token=token)
        )
    
    async def moderate_content(
        self,
        content_type: str,
        content_data: Dict[str, Any],
        token: str
    ) -> Dict[str, Any]:
        """
        Модерация контента.
        
        Args:
            content_type: Тип контента
            content_data: Данные контента
            token: JWT токен
            
        Returns:
            Dict[str, Any]: Результат модерации
        """
        client = self.get_client("moderation-svc")
        
        response = await client.post(
            "/api/v1/moderation/requests",
            data={
                "content_type": content_type,
                "content_data": content_data
            },
            config=RequestConfig(auth_token=token)
        )
        
        return response["data"]
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики всех клиентов."""
        return self.client_manager.get_all_stats()
