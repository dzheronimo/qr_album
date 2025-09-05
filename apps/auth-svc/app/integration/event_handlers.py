"""
Обработчики событий для auth-svc.

Содержит логику обработки событий от других сервисов.
"""

import logging
from typing import Dict, Any

from packages.py_commons.integration import Event, EventTypes

logger = logging.getLogger(__name__)


class EventHandlers:
    """Обработчики событий для auth-svc."""
    
    def __init__(self):
        """Инициализация обработчиков событий."""
        self.handlers = {
            EventTypes.USER_REGISTERED: [self._handle_user_registered],
            EventTypes.USER_LOGIN: [self._handle_user_login],
            EventTypes.USER_LOGOUT: [self._handle_user_logout],
            EventTypes.USER_PROFILE_UPDATED: [self._handle_user_profile_updated],
        }
    
    async def _handle_user_registered(self, event: Event) -> None:
        """
        Обработка события регистрации пользователя.
        
        Args:
            event: Событие регистрации
        """
        try:
            user_id = event.data.get("user_id")
            user_data = event.data.get("user_data", {})
            
            logger.info(f"User {user_id} registered: {user_data}")
            
            # Здесь можно добавить логику:
            # - Отправка приветственного письма
            # - Создание профиля пользователя
            # - Настройка уведомлений
            # - Инициализация аналитики
            
        except Exception as e:
            logger.error(f"Error handling user registration event: {e}")
    
    async def _handle_user_login(self, event: Event) -> None:
        """
        Обработка события входа пользователя.
        
        Args:
            event: Событие входа
        """
        try:
            user_id = event.data.get("user_id")
            login_data = event.data.get("login_data", {})
            
            logger.info(f"User {user_id} logged in: {login_data}")
            
            # Здесь можно добавить логику:
            # - Обновление статистики входов
            # - Проверка подозрительной активности
            # - Отправка уведомления о входе
            
        except Exception as e:
            logger.error(f"Error handling user login event: {e}")
    
    async def _handle_user_logout(self, event: Event) -> None:
        """
        Обработка события выхода пользователя.
        
        Args:
            event: Событие выхода
        """
        try:
            user_id = event.data.get("user_id")
            logout_data = event.data.get("logout_data", {})
            
            logger.info(f"User {user_id} logged out: {logout_data}")
            
            # Здесь можно добавить логику:
            # - Инвалидация сессий
            # - Обновление статистики
            # - Очистка временных данных
            
        except Exception as e:
            logger.error(f"Error handling user logout event: {e}")
    
    async def _handle_user_profile_updated(self, event: Event) -> None:
        """
        Обработка события обновления профиля пользователя.
        
        Args:
            event: Событие обновления профиля
        """
        try:
            user_id = event.data.get("user_id")
            profile_data = event.data.get("profile_data", {})
            
            logger.info(f"User {user_id} profile updated: {profile_data}")
            
            # Здесь можно добавить логику:
            # - Обновление кэша пользователя
            # - Проверка изменений безопасности
            # - Уведомление о критических изменениях
            
        except Exception as e:
            logger.error(f"Error handling user profile update event: {e}")
    
    def get_handlers(self) -> Dict[str, list]:
        """
        Получение всех обработчиков событий.
        
        Returns:
            Dict[str, list]: Словарь обработчиков по типам событий
        """
        return self.handlers
