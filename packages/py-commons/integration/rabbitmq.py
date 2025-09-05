"""
RabbitMQ клиент для интеграции между сервисами.

Содержит утилиты для публикации и потребления событий.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Callable, List
from datetime import datetime
from dataclasses import dataclass, asdict

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractIncomingMessage

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Модель события для RabbitMQ."""
    event_type: str
    service_name: str
    data: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь."""
        return {
            "event_type": self.event_type,
            "service_name": self.service_name,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "reply_to": self.reply_to
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """Создание из словаря."""
        return cls(
            event_type=data["event_type"],
            service_name=data["service_name"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=data.get("correlation_id"),
            reply_to=data.get("reply_to")
        )


class RabbitMQClient:
    """Клиент для работы с RabbitMQ."""
    
    def __init__(
        self,
        connection_url: str,
        service_name: str,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Инициализация клиента.
        
        Args:
            connection_url: URL подключения к RabbitMQ
            service_name: Название сервиса
            max_retries: Максимальное количество попыток переподключения
            retry_delay: Задержка между попытками
        """
        self.connection_url = connection_url
        self.service_name = service_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchanges: Dict[str, aio_pika.Exchange] = {}
        self.queues: Dict[str, aio_pika.Queue] = {}
        
        self._is_connected = False
    
    async def connect(self) -> None:
        """Подключение к RabbitMQ."""
        for attempt in range(self.max_retries):
            try:
                self.connection = await aio_pika.connect_robust(
                    self.connection_url,
                    client_properties={
                        "connection_name": f"{self.service_name}-client"
                    }
                )
                
                self.channel = await self.connection.channel()
                await self.channel.set_qos(prefetch_count=10)
                
                self._is_connected = True
                logger.info(f"Connected to RabbitMQ for service {self.service_name}")
                return
                
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise
    
    async def disconnect(self) -> None:
        """Отключение от RabbitMQ."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            self._is_connected = False
            logger.info(f"Disconnected from RabbitMQ for service {self.service_name}")
    
    async def ensure_connected(self) -> None:
        """Проверка и восстановление подключения."""
        if not self._is_connected or self.connection.is_closed:
            await self.connect()
    
    async def declare_exchange(
        self,
        name: str,
        exchange_type: ExchangeType = ExchangeType.TOPIC,
        durable: bool = True
    ) -> aio_pika.Exchange:
        """
        Объявление обменника.
        
        Args:
            name: Название обменника
            exchange_type: Тип обменника
            durable: Долговечность
            
        Returns:
            aio_pika.Exchange: Обменник
        """
        await self.ensure_connected()
        
        if name not in self.exchanges:
            exchange = await self.channel.declare_exchange(
                name=name,
                type=exchange_type,
                durable=durable
            )
            self.exchanges[name] = exchange
            logger.info(f"Declared exchange: {name}")
        
        return self.exchanges[name]
    
    async def declare_queue(
        self,
        name: str,
        durable: bool = True,
        exclusive: bool = False,
        auto_delete: bool = False,
        arguments: Optional[Dict[str, Any]] = None
    ) -> aio_pika.Queue:
        """
        Объявление очереди.
        
        Args:
            name: Название очереди
            durable: Долговечность
            exclusive: Эксклюзивность
            auto_delete: Автоудаление
            arguments: Дополнительные аргументы
            
        Returns:
            aio_pika.Queue: Очередь
        """
        await self.ensure_connected()
        
        if name not in self.queues:
            queue = await self.channel.declare_queue(
                name=name,
                durable=durable,
                exclusive=exclusive,
                auto_delete=auto_delete,
                arguments=arguments or {}
            )
            self.queues[name] = queue
            logger.info(f"Declared queue: {name}")
        
        return self.queues[name]
    
    async def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str
    ) -> None:
        """
        Привязка очереди к обменнику.
        
        Args:
            queue_name: Название очереди
            exchange_name: Название обменника
            routing_key: Ключ маршрутизации
        """
        await self.ensure_connected()
        
        queue = await self.declare_queue(queue_name)
        exchange = await self.declare_exchange(exchange_name)
        
        await queue.bind(exchange, routing_key)
        logger.info(f"Bound queue {queue_name} to exchange {exchange_name} with key {routing_key}")


class EventPublisher:
    """Публикатор событий."""
    
    def __init__(self, rabbitmq_client: RabbitMQClient):
        """
        Инициализация публикатора.
        
        Args:
            rabbitmq_client: Клиент RabbitMQ
        """
        self.client = rabbitmq_client
    
    async def publish_event(
        self,
        event: Event,
        exchange_name: str = "events",
        routing_key: Optional[str] = None
    ) -> None:
        """
        Публикация события.
        
        Args:
            event: Событие для публикации
            exchange_name: Название обменника
            routing_key: Ключ маршрутизации
        """
        await self.client.ensure_connected()
        
        exchange = await self.client.declare_exchange(exchange_name)
        
        # Используем тип события как ключ маршрутизации, если не указан
        if routing_key is None:
            routing_key = event.event_type
        
        message = Message(
            json.dumps(event.to_dict()).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            correlation_id=event.correlation_id,
            reply_to=event.reply_to
        )
        
        await exchange.publish(message, routing_key=routing_key)
        logger.info(f"Published event {event.event_type} to {exchange_name} with key {routing_key}")
    
    async def publish_user_event(
        self,
        event_type: str,
        user_id: int,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Публикация события пользователя.
        
        Args:
            event_type: Тип события
            user_id: ID пользователя
            data: Данные события
            correlation_id: ID корреляции
        """
        event = Event(
            event_type=event_type,
            service_name=self.client.service_name,
            data={"user_id": user_id, **data},
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id
        )
        
        await self.publish_event(event, routing_key=f"user.{user_id}.{event_type}")
    
    async def publish_system_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Публикация системного события.
        
        Args:
            event_type: Тип события
            data: Данные события
            correlation_id: ID корреляции
        """
        event = Event(
            event_type=event_type,
            service_name=self.client.service_name,
            data=data,
            timestamp=datetime.utcnow(),
            correlation_id=correlation_id
        )
        
        await self.publish_event(event, routing_key=f"system.{event_type}")


class EventConsumer:
    """Потребитель событий."""
    
    def __init__(self, rabbitmq_client: RabbitMQClient):
        """
        Инициализация потребителя.
        
        Args:
            rabbitmq_client: Клиент RabbitMQ
        """
        self.client = rabbitmq_client
        self.handlers: Dict[str, List[Callable]] = {}
        self.consuming = False
    
    def register_handler(
        self,
        event_type: str,
        handler: Callable[[Event], None]
    ) -> None:
        """
        Регистрация обработчика события.
        
        Args:
            event_type: Тип события
            handler: Обработчик события
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")
    
    async def start_consuming(
        self,
        queue_name: str,
        exchange_name: str = "events",
        routing_key: str = "*"
    ) -> None:
        """
        Начало потребления событий.
        
        Args:
            queue_name: Название очереди
            exchange_name: Название обменника
            routing_key: Ключ маршрутизации
        """
        await self.client.ensure_connected()
        
        # Объявляем очередь и привязываем к обменнику
        await self.client.bind_queue(queue_name, exchange_name, routing_key)
        queue = self.client.queues[queue_name]
        
        # Начинаем потребление
        await queue.consume(self._process_message)
        self.consuming = True
        logger.info(f"Started consuming from queue {queue_name}")
    
    async def stop_consuming(self) -> None:
        """Остановка потребления событий."""
        self.consuming = False
        logger.info("Stopped consuming events")
    
    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        """
        Обработка входящего сообщения.
        
        Args:
            message: Входящее сообщение
        """
        try:
            # Парсим событие
            event_data = json.loads(message.body.decode())
            event = Event.from_dict(event_data)
            
            # Вызываем обработчики
            if event.event_type in self.handlers:
                for handler in self.handlers[event.event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event.event_type}: {e}")
            
            # Подтверждаем обработку
            message.ack()
            logger.debug(f"Processed event: {event.event_type}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            message.nack(requeue=False)
    
    async def consume_user_events(
        self,
        user_id: int,
        event_types: List[str]
    ) -> None:
        """
        Потребление событий пользователя.
        
        Args:
            user_id: ID пользователя
            event_types: Типы событий
        """
        queue_name = f"user_{user_id}_events"
        
        for event_type in event_types:
            routing_key = f"user.{user_id}.{event_type}"
            await self.start_consuming(queue_name, routing_key=routing_key)
    
    async def consume_system_events(
        self,
        event_types: List[str]
    ) -> None:
        """
        Потребление системных событий.
        
        Args:
            event_types: Типы событий
        """
        queue_name = f"{self.client.service_name}_system_events"
        
        for event_type in event_types:
            routing_key = f"system.{event_type}"
            await self.start_consuming(queue_name, routing_key=routing_key)


# Предопределенные типы событий
class EventTypes:
    """Типы событий в системе."""
    
    # События пользователей
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_PROFILE_UPDATED = "user.profile.updated"
    
    # События альбомов
    ALBUM_CREATED = "album.created"
    ALBUM_UPDATED = "album.updated"
    ALBUM_DELETED = "album.deleted"
    PAGE_CREATED = "page.created"
    PAGE_UPDATED = "page.updated"
    PAGE_DELETED = "page.deleted"
    
    # События медиа
    MEDIA_UPLOADED = "media.uploaded"
    MEDIA_DELETED = "media.deleted"
    
    # События QR кодов
    QR_CODE_GENERATED = "qr.generated"
    QR_CODE_SCANNED = "qr.scanned"
    
    # События аналитики
    ANALYTICS_EVENT = "analytics.event"
    
    # События биллинга
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    PAYMENT_PROCESSED = "payment.processed"
    
    # События уведомлений
    NOTIFICATION_SENT = "notification.sent"
    
    # События модерации
    CONTENT_MODERATED = "content.moderated"
    
    # События печати
    PRINT_JOB_CREATED = "print.job.created"
    PRINT_JOB_COMPLETED = "print.job.completed"
