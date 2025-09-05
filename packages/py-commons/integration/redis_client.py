"""
Redis клиент для кэширования и межсервисного взаимодействия.

Содержит утилиты для работы с Redis.
"""

import asyncio
import json
import logging
import pickle
from typing import Any, Dict, Optional, List, Union, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Конфигурация кэша."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 10
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    decode_responses: bool = True


class RedisClient:
    """Клиент для работы с Redis."""
    
    def __init__(self, config: CacheConfig):
        """
        Инициализация клиента.
        
        Args:
            config: Конфигурация Redis
        """
        self.config = config
        self.redis: Optional[Redis] = None
        self._is_connected = False
    
    async def connect(self) -> None:
        """Подключение к Redis."""
        try:
            pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                decode_responses=self.config.decode_responses
            )
            
            self.redis = Redis(connection_pool=pool)
            
            # Проверяем подключение
            await self.redis.ping()
            self._is_connected = True
            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Отключение от Redis."""
        if self.redis:
            await self.redis.close()
            self._is_connected = False
            logger.info("Disconnected from Redis")
    
    async def ensure_connected(self) -> None:
        """Проверка и восстановление подключения."""
        if not self._is_connected:
            await self.connect()
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        serialize: bool = True
    ) -> bool:
        """
        Установка значения в кэш.
        
        Args:
            key: Ключ
            value: Значение
            expire: Время жизни в секундах
            serialize: Сериализовать ли значение
            
        Returns:
            bool: True если успешно
        """
        await self.ensure_connected()
        
        try:
            if serialize:
                value = json.dumps(value, default=str)
            
            result = await self.redis.set(key, value, ex=expire)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False
    
    async def get(
        self,
        key: str,
        deserialize: bool = True,
        default: Any = None
    ) -> Any:
        """
        Получение значения из кэша.
        
        Args:
            key: Ключ
            deserialize: Десериализовать ли значение
            default: Значение по умолчанию
            
        Returns:
            Any: Значение или default
        """
        await self.ensure_connected()
        
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            
            if deserialize:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            
            return value
            
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return default
    
    async def delete(self, *keys: str) -> int:
        """
        Удаление ключей из кэша.
        
        Args:
            *keys: Ключи для удаления
            
        Returns:
            int: Количество удаленных ключей
        """
        await self.ensure_connected()
        
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Failed to delete keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """
        Проверка существования ключа.
        
        Args:
            key: Ключ
            
        Returns:
            bool: True если ключ существует
        """
        await self.ensure_connected()
        
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Установка времени жизни ключа.
        
        Args:
            key: Ключ
            seconds: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        await self.ensure_connected()
        
        try:
            return bool(await self.redis.expire(key, seconds))
        except Exception as e:
            logger.error(f"Failed to set expire for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """
        Получение времени жизни ключа.
        
        Args:
            key: Ключ
            
        Returns:
            int: Время жизни в секундах (-1 если не установлено, -2 если не существует)
        """
        await self.ensure_connected()
        
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return -2
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """
        Получение ключей по шаблону.
        
        Args:
            pattern: Шаблон поиска
            
        Returns:
            List[str]: Список ключей
        """
        await self.ensure_connected()
        
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {e}")
            return []
    
    async def flushdb(self) -> bool:
        """
        Очистка текущей базы данных.
        
        Returns:
            bool: True если успешно
        """
        await self.ensure_connected()
        
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Failed to flush database: {e}")
            return False


class CacheManager:
    """Менеджер кэширования с поддержкой различных стратегий."""
    
    def __init__(self, redis_client: RedisClient, default_ttl: int = 3600):
        """
        Инициализация менеджера кэша.
        
        Args:
            redis_client: Redis клиент
            default_ttl: Время жизни по умолчанию в секундах
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _make_key(self, prefix: str, *parts: str) -> str:
        """
        Создание ключа кэша.
        
        Args:
            prefix: Префикс
            *parts: Части ключа
            
        Returns:
            str: Ключ кэша
        """
        return f"{prefix}:{':'.join(str(part) for part in parts)}"
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None,
        prefix: str = "cache"
    ) -> Any:
        """
        Получение значения из кэша или создание нового.
        
        Args:
            key: Ключ кэша
            factory: Функция для создания значения
            ttl: Время жизни в секундах
            prefix: Префикс ключа
            
        Returns:
            Any: Значение из кэша или новое значение
        """
        cache_key = self._make_key(prefix, key)
        
        # Пытаемся получить из кэша
        value = await self.redis.get(cache_key)
        if value is not None:
            self._cache_stats["hits"] += 1
            return value
        
        # Создаем новое значение
        self._cache_stats["misses"] += 1
        value = factory()
        
        # Сохраняем в кэш
        await self.redis.set(cache_key, value, expire=ttl or self.default_ttl)
        self._cache_stats["sets"] += 1
        
        return value
    
    async def invalidate(self, pattern: str, prefix: str = "cache") -> int:
        """
        Инвалидация кэша по шаблону.
        
        Args:
            pattern: Шаблон ключей
            prefix: Префикс ключей
            
        Returns:
            int: Количество удаленных ключей
        """
        cache_pattern = self._make_key(prefix, pattern)
        keys = await self.redis.keys(cache_pattern)
        
        if keys:
            deleted = await self.redis.delete(*keys)
            self._cache_stats["deletes"] += deleted
            return deleted
        
        return 0
    
    async def cache_user_data(
        self,
        user_id: int,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование данных пользователя.
        
        Args:
            user_id: ID пользователя
            data: Данные пользователя
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis.set(
            self._make_key("user", user_id),
            data,
            expire=ttl or self.default_ttl
        )
    
    async def get_user_data(
        self,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получение данных пользователя из кэша.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Dict[str, Any]]: Данные пользователя или None
        """
        return await self.redis.get(self._make_key("user", user_id))
    
    async def cache_album_data(
        self,
        album_id: int,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование данных альбома.
        
        Args:
            album_id: ID альбома
            data: Данные альбома
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis.set(
            self._make_key("album", album_id),
            data,
            expire=ttl or self.default_ttl
        )
    
    async def get_album_data(
        self,
        album_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Получение данных альбома из кэша.
        
        Args:
            album_id: ID альбома
            
        Returns:
            Optional[Dict[str, Any]]: Данные альбома или None
        """
        return await self.redis.get(self._make_key("album", album_id))
    
    async def cache_qr_data(
        self,
        qr_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование данных QR кода.
        
        Args:
            qr_id: ID QR кода
            data: Данные QR кода
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis.set(
            self._make_key("qr", qr_id),
            data,
            expire=ttl or self.default_ttl
        )
    
    async def get_qr_data(
        self,
        qr_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение данных QR кода из кэша.
        
        Args:
            qr_id: ID QR кода
            
        Returns:
            Optional[Dict[str, Any]]: Данные QR кода или None
        """
        return await self.redis.get(self._make_key("qr", qr_id))
    
    async def cache_analytics_data(
        self,
        key: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширование данных аналитики.
        
        Args:
            key: Ключ аналитики
            data: Данные аналитики
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        return await self.redis.set(
            self._make_key("analytics", key),
            data,
            expire=ttl or self.default_ttl
        )
    
    async def get_analytics_data(
        self,
        key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение данных аналитики из кэша.
        
        Args:
            key: Ключ аналитики
            
        Returns:
            Optional[Dict[str, Any]]: Данные аналитики или None
        """
        return await self.redis.get(self._make_key("analytics", key))
    
    async def invalidate_user_cache(self, user_id: int) -> int:
        """
        Инвалидация кэша пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            int: Количество удаленных ключей
        """
        return await self.invalidate(f"user:{user_id}")
    
    async def invalidate_album_cache(self, album_id: int) -> int:
        """
        Инвалидация кэша альбома.
        
        Args:
            album_id: ID альбома
            
        Returns:
            int: Количество удаленных ключей
        """
        return await self.invalidate(f"album:{album_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша."""
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = self._cache_stats["hits"] / max(total_requests, 1)
        
        return {
            "hits": self._cache_stats["hits"],
            "misses": self._cache_stats["misses"],
            "sets": self._cache_stats["sets"],
            "deletes": self._cache_stats["deletes"],
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }


# Утилиты для работы с сессиями
class SessionManager:
    """Менеджер сессий пользователей."""
    
    def __init__(self, redis_client: RedisClient, session_ttl: int = 86400):
        """
        Инициализация менеджера сессий.
        
        Args:
            redis_client: Redis клиент
            session_ttl: Время жизни сессии в секундах
        """
        self.redis = redis_client
        self.session_ttl = session_ttl
    
    async def create_session(
        self,
        user_id: int,
        session_data: Dict[str, Any]
    ) -> str:
        """
        Создание сессии пользователя.
        
        Args:
            user_id: ID пользователя
            session_data: Данные сессии
            
        Returns:
            str: ID сессии
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        session_key = f"session:{session_id}"
        session_data["user_id"] = user_id
        session_data["created_at"] = datetime.utcnow().isoformat()
        
        await self.redis.set(session_key, session_data, expire=self.session_ttl)
        
        # Сохраняем связь пользователь -> сессия
        user_sessions_key = f"user_sessions:{user_id}"
        await self.redis.sadd(user_sessions_key, session_id)
        await self.redis.expire(user_sessions_key, self.session_ttl)
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение сессии по ID.
        
        Args:
            session_id: ID сессии
            
        Returns:
            Optional[Dict[str, Any]]: Данные сессии или None
        """
        session_key = f"session:{session_id}"
        return await self.redis.get(session_key)
    
    async def update_session(
        self,
        session_id: str,
        session_data: Dict[str, Any]
    ) -> bool:
        """
        Обновление сессии.
        
        Args:
            session_id: ID сессии
            session_data: Новые данные сессии
            
        Returns:
            bool: True если успешно
        """
        session_key = f"session:{session_id}"
        session_data["updated_at"] = datetime.utcnow().isoformat()
        
        return await self.redis.set(session_key, session_data, expire=self.session_ttl)
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Удаление сессии.
        
        Args:
            session_id: ID сессии
            
        Returns:
            bool: True если успешно
        """
        session_key = f"session:{session_id}"
        
        # Получаем данные сессии для удаления связи с пользователем
        session_data = await self.redis.get(session_key)
        if session_data and "user_id" in session_data:
            user_sessions_key = f"user_sessions:{session_data['user_id']}"
            await self.redis.srem(user_sessions_key, session_id)
        
        return await self.redis.delete(session_key)
    
    async def delete_user_sessions(self, user_id: int) -> int:
        """
        Удаление всех сессий пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            int: Количество удаленных сессий
        """
        user_sessions_key = f"user_sessions:{user_id}"
        session_ids = await self.redis.smembers(user_sessions_key)
        
        if session_ids:
            # Удаляем все сессии
            session_keys = [f"session:{session_id}" for session_id in session_ids]
            await self.redis.delete(*session_keys)
            
            # Удаляем связь с пользователем
            await self.redis.delete(user_sessions_key)
            
            return len(session_ids)
        
        return 0
