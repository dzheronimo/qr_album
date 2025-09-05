"""
Менеджер кэширования для auth-svc.

Содержит настройки и утилиты для работы с Redis кэшем.
"""

import logging
from typing import Dict, Any, Optional

from packages.py_commons.integration import (
    RedisClient, CacheConfig, CacheManager, SessionManager
)

logger = logging.getLogger(__name__)


class AuthCacheManager:
    """Менеджер кэширования для auth-svc."""
    
    def __init__(self, redis_config: CacheConfig):
        """
        Инициализация менеджера кэша.
        
        Args:
            redis_config: Конфигурация Redis
        """
        self.redis_client = RedisClient(redis_config)
        self.cache_manager = CacheManager(self.redis_client, default_ttl=3600)
        self.session_manager = SessionManager(self.redis_client, session_ttl=86400)
        
        self._is_connected = False
    
    async def connect(self) -> None:
        """Подключение к Redis."""
        await self.redis_client.connect()
        self._is_connected = True
        logger.info("Auth cache manager connected to Redis")
    
    async def disconnect(self) -> None:
        """Отключение от Redis."""
        await self.redis_client.disconnect()
        self._is_connected = False
        logger.info("Auth cache manager disconnected from Redis")
    
    async def cache_user_auth_data(
        self,
        user_id: int,
        auth_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование данных аутентификации пользователя.
        
        Args:
            user_id: ID пользователя
            auth_data: Данные аутентификации
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.cache_manager.cache_user_data(user_id, auth_data, ttl)
    
    async def get_user_auth_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение данных аутентификации пользователя из кэша.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Dict[str, Any]]: Данные аутентификации или None
        """
        return await self.cache_manager.get_user_data(user_id)
    
    async def cache_user_permissions(
        self,
        user_id: int,
        permissions: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование разрешений пользователя.
        
        Args:
            user_id: ID пользователя
            permissions: Разрешения пользователя
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis_client.set(
            f"user_permissions:{user_id}",
            permissions,
            expire=ttl or 1800  # 30 минут по умолчанию
        )
    
    async def get_user_permissions(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение разрешений пользователя из кэша.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Dict[str, Any]]: Разрешения пользователя или None
        """
        return await self.redis_client.get(f"user_permissions:{user_id}")
    
    async def cache_user_roles(
        self,
        user_id: int,
        roles: list,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование ролей пользователя.
        
        Args:
            user_id: ID пользователя
            roles: Роли пользователя
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis_client.set(
            f"user_roles:{user_id}",
            roles,
            expire=ttl or 1800  # 30 минут по умолчанию
        )
    
    async def get_user_roles(self, user_id: int) -> Optional[list]:
        """
        Получение ролей пользователя из кэша.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[list]: Роли пользователя или None
        """
        return await self.redis_client.get(f"user_roles:{user_id}")
    
    async def cache_token_blacklist(
        self,
        token_hash: str,
        expire_time: int
    ) -> bool:
        """
        Добавление токена в черный список.
        
        Args:
            token_hash: Хэш токена
            expire_time: Время истечения токена
            
        Returns:
            bool: True если успешно
        """
        return await self.redis_client.set(
            f"blacklist:{token_hash}",
            True,
            expire=expire_time
        )
    
    async def is_token_blacklisted(self, token_hash: str) -> bool:
        """
        Проверка, находится ли токен в черном списке.
        
        Args:
            token_hash: Хэш токена
            
        Returns:
            bool: True если токен в черном списке
        """
        return await self.redis_client.exists(f"blacklist:{token_hash}")
    
    async def cache_login_attempts(
        self,
        user_id: int,
        attempts: int,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование попыток входа пользователя.
        
        Args:
            user_id: ID пользователя
            attempts: Количество попыток
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis_client.set(
            f"login_attempts:{user_id}",
            attempts,
            expire=ttl or 3600  # 1 час по умолчанию
        )
    
    async def get_login_attempts(self, user_id: int) -> int:
        """
        Получение количества попыток входа пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            int: Количество попыток входа
        """
        attempts = await self.redis_client.get(f"login_attempts:{user_id}")
        return attempts if attempts is not None else 0
    
    async def increment_login_attempts(self, user_id: int) -> int:
        """
        Увеличение количества попыток входа пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            int: Новое количество попыток
        """
        current_attempts = await self.get_login_attempts(user_id)
        new_attempts = current_attempts + 1
        
        await self.cache_login_attempts(user_id, new_attempts)
        return new_attempts
    
    async def reset_login_attempts(self, user_id: int) -> bool:
        """
        Сброс количества попыток входа пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если успешно
        """
        return await self.redis_client.delete(f"login_attempts:{user_id}")
    
    async def cache_password_reset_token(
        self,
        token: str,
        user_id: int,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование токена сброса пароля.
        
        Args:
            token: Токен сброса пароля
            user_id: ID пользователя
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis_client.set(
            f"password_reset:{token}",
            user_id,
            expire=ttl or 3600  # 1 час по умолчанию
        )
    
    async def get_password_reset_user_id(self, token: str) -> Optional[int]:
        """
        Получение ID пользователя по токену сброса пароля.
        
        Args:
            token: Токен сброса пароля
            
        Returns:
            Optional[int]: ID пользователя или None
        """
        return await self.redis_client.get(f"password_reset:{token}")
    
    async def delete_password_reset_token(self, token: str) -> bool:
        """
        Удаление токена сброса пароля.
        
        Args:
            token: Токен сброса пароля
            
        Returns:
            bool: True если успешно
        """
        return await self.redis_client.delete(f"password_reset:{token}")
    
    async def invalidate_user_cache(self, user_id: int) -> int:
        """
        Инвалидация всего кэша пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            int: Количество удаленных ключей
        """
        # Удаляем все ключи, связанные с пользователем
        keys_to_delete = [
            f"user:{user_id}",
            f"user_permissions:{user_id}",
            f"user_roles:{user_id}",
            f"login_attempts:{user_id}"
        ]
        
        deleted_count = await self.redis_client.delete(*keys_to_delete)
        
        # Также инвалидируем через cache_manager
        cache_deleted = await self.cache_manager.invalidate_user_cache(user_id)
        
        return deleted_count + cache_deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша."""
        return {
            "cache_stats": self.cache_manager.get_stats(),
            "redis_connected": self._is_connected
        }
