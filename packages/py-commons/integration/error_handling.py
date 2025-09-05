"""
Обработка ошибок для межсервисного взаимодействия.

Содержит утилиты для обработки ошибок, повторных попыток и circuit breaker.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Optional, Dict, List, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Типы ошибок."""
    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    INTERNAL = "internal"
    EXTERNAL = "external"


@dataclass
class IntegrationError(Exception):
    """Ошибка интеграции между сервисами."""
    error_type: ErrorType
    service_name: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retryable: bool = True
    status_code: Optional[int] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def __str__(self) -> str:
        return f"[{self.service_name}] {self.error_type.value}: {self.message}"


@dataclass
class RetryConfig:
    """Конфигурация повторных попыток."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_errors: List[ErrorType] = None
    
    def __post_init__(self):
        if self.retryable_errors is None:
            self.retryable_errors = [
                ErrorType.NETWORK,
                ErrorType.TIMEOUT,
                ErrorType.RATE_LIMIT,
                ErrorType.INTERNAL
            ]


class RetryManager:
    """Менеджер повторных попыток."""
    
    def __init__(self, config: RetryConfig):
        """
        Инициализация менеджера повторных попыток.
        
        Args:
            config: Конфигурация повторных попыток
        """
        self.config = config
        self._stats = {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "retries": 0
        }
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Выполнение функции с повторными попытками.
        
        Args:
            func: Функция для выполнения
            *args: Аргументы функции
            **kwargs: Ключевые аргументы функции
            
        Returns:
            Any: Результат выполнения функции
            
        Raises:
            IntegrationError: Ошибка после всех попыток
        """
        last_error = None
        
        for attempt in range(self.config.max_attempts):
            try:
                self._stats["total_attempts"] += 1
                
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                self._stats["successful_attempts"] += 1
                return result
                
            except Exception as e:
                last_error = e
                self._stats["failed_attempts"] += 1
                
                # Проверяем, можно ли повторить попытку
                if not self._should_retry(e, attempt):
                    break
                
                # Вычисляем задержку
                delay = self._calculate_delay(attempt)
                
                if attempt < self.config.max_attempts - 1:
                    self._stats["retries"] += 1
                    logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}"
                    )
                    await asyncio.sleep(delay)
        
        # Если все попытки исчерпаны, поднимаем ошибку
        if isinstance(last_error, IntegrationError):
            raise last_error
        else:
            raise IntegrationError(
                error_type=ErrorType.INTERNAL,
                service_name="unknown",
                message=f"Function execution failed after {self.config.max_attempts} attempts",
                details={"original_error": str(last_error)},
                retryable=False
            )
    
    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Проверка, можно ли повторить попытку.
        
        Args:
            error: Ошибка
            attempt: Номер попытки
            
        Returns:
            bool: True если можно повторить
        """
        if attempt >= self.config.max_attempts - 1:
            return False
        
        if isinstance(error, IntegrationError):
            return error.retryable and error.error_type in self.config.retryable_errors
        
        # Для других ошибок считаем, что можно повторить
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Вычисление задержки между попытками.
        
        Args:
            attempt: Номер попытки
            
        Returns:
            float: Задержка в секундах
        """
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        
        if self.config.jitter:
            # Добавляем случайную составляющую (±25%)
            import random
            jitter = delay * 0.25 * (2 * random.random() - 1)
            delay += jitter
        
        return max(0, delay)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики повторных попыток."""
        total_attempts = self._stats["total_attempts"]
        success_rate = self._stats["successful_attempts"] / max(total_attempts, 1)
        
        return {
            **self._stats,
            "success_rate": success_rate,
            "retry_rate": self._stats["retries"] / max(total_attempts, 1)
        }


class CircuitBreakerState(Enum):
    """Состояния circuit breaker."""
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"          # Блокировка запросов
    HALF_OPEN = "half_open"  # Тестирование восстановления


@dataclass
class CircuitBreakerConfig:
    """Конфигурация circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception
    success_threshold: int = 3


class CircuitBreaker:
    """Circuit breaker для защиты от каскадных сбоев."""
    
    def __init__(self, config: CircuitBreakerConfig):
        """
        Инициализация circuit breaker.
        
        Args:
            config: Конфигурация circuit breaker
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opened": 0,
            "circuit_closed": 0
        }
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Выполнение функции через circuit breaker.
        
        Args:
            func: Функция для выполнения
            *args: Аргументы функции
            **kwargs: Ключевые аргументы функции
            
        Returns:
            Any: Результат выполнения функции
            
        Raises:
            IntegrationError: Ошибка circuit breaker или функции
        """
        self._stats["total_requests"] += 1
        
        # Проверяем состояние circuit breaker
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                logger.info("Circuit breaker moved to HALF_OPEN state")
            else:
                self._stats["circuit_opened"] += 1
                raise IntegrationError(
                    error_type=ErrorType.EXTERNAL,
                    service_name="circuit_breaker",
                    message="Circuit breaker is OPEN",
                    retryable=False
                )
        
        # Выполняем функцию
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """
        Проверка, можно ли попытаться сбросить circuit breaker.
        
        Returns:
            bool: True если можно попытаться
        """
        if self.last_failure_time is None:
            return True
        
        return (datetime.utcnow() - self.last_failure_time).total_seconds() >= self.config.recovery_timeout
    
    def _on_success(self) -> None:
        """Обработка успешного выполнения."""
        self._stats["successful_requests"] += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self._stats["circuit_closed"] += 1
                logger.info("Circuit breaker moved to CLOSED state")
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Обработка неудачного выполнения."""
        self._stats["failed_requests"] += 1
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning("Circuit breaker moved to OPEN state after failure in HALF_OPEN")
        elif self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                self._stats["circuit_opened"] += 1
                logger.warning("Circuit breaker moved to OPEN state")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики circuit breaker."""
        total_requests = self._stats["total_requests"]
        success_rate = self._stats["successful_requests"] / max(total_requests, 1)
        
        return {
            **self._stats,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "success_rate": success_rate
        }


class ErrorHandler:
    """Обработчик ошибок для межсервисного взаимодействия."""
    
    def __init__(self):
        """Инициализация обработчика ошибок."""
        self.error_handlers: Dict[ErrorType, List[Callable]] = {}
        self._stats = {
            "total_errors": 0,
            "handled_errors": 0,
            "unhandled_errors": 0
        }
    
    def register_handler(
        self,
        error_type: ErrorType,
        handler: Callable[[IntegrationError], None]
    ) -> None:
        """
        Регистрация обработчика ошибки.
        
        Args:
            error_type: Тип ошибки
            handler: Обработчик ошибки
        """
        if error_type not in self.error_handlers:
            self.error_handlers[error_type] = []
        
        self.error_handlers[error_type].append(handler)
        logger.info(f"Registered error handler for {error_type.value}")
    
    async def handle_error(self, error: IntegrationError) -> None:
        """
        Обработка ошибки.
        
        Args:
            error: Ошибка для обработки
        """
        self._stats["total_errors"] += 1
        
        if error.error_type in self.error_handlers:
            self._stats["handled_errors"] += 1
            
            for handler in self.error_handlers[error.error_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(error)
                    else:
                        handler(error)
                except Exception as e:
                    logger.error(f"Error in error handler: {e}")
        else:
            self._stats["unhandled_errors"] += 1
            logger.warning(f"Unhandled error: {error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики обработки ошибок."""
        total_errors = self._stats["total_errors"]
        handled_rate = self._stats["handled_errors"] / max(total_errors, 1)
        
        return {
            **self._stats,
            "handled_rate": handled_rate
        }


# Утилиты для создания ошибок
class ErrorFactory:
    """Фабрика для создания ошибок интеграции."""
    
    @staticmethod
    def create_network_error(
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> IntegrationError:
        """Создание ошибки сети."""
        return IntegrationError(
            error_type=ErrorType.NETWORK,
            service_name=service_name,
            message=message,
            details=details,
            retryable=True
        )
    
    @staticmethod
    def create_timeout_error(
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> IntegrationError:
        """Создание ошибки таймаута."""
        return IntegrationError(
            error_type=ErrorType.TIMEOUT,
            service_name=service_name,
            message=message,
            details=details,
            retryable=True
        )
    
    @staticmethod
    def create_auth_error(
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> IntegrationError:
        """Создание ошибки аутентификации."""
        return IntegrationError(
            error_type=ErrorType.AUTHENTICATION,
            service_name=service_name,
            message=message,
            details=details,
            retryable=False
        )
    
    @staticmethod
    def create_validation_error(
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> IntegrationError:
        """Создание ошибки валидации."""
        return IntegrationError(
            error_type=ErrorType.VALIDATION,
            service_name=service_name,
            message=message,
            details=details,
            retryable=False
        )
    
    @staticmethod
    def create_not_found_error(
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> IntegrationError:
        """Создание ошибки "не найдено"."""
        return IntegrationError(
            error_type=ErrorType.NOT_FOUND,
            service_name=service_name,
            message=message,
            details=details,
            retryable=False
        )
    
    @staticmethod
    def create_rate_limit_error(
        service_name: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> IntegrationError:
        """Создание ошибки лимита запросов."""
        return IntegrationError(
            error_type=ErrorType.RATE_LIMIT,
            service_name=service_name,
            message=message,
            details=details,
            retryable=True
        )
