"""
Сервис аутентификации.

Содержит бизнес-логику для аутентификации и авторизации пользователей.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user_service import UserService
from app.commons.security import create_access_token, create_refresh_token
from app.config import Settings

settings = Settings()


class AuthService:
    """Сервис аутентификации."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.user_service = UserService(db)
    
    async def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Вход пользователя в систему.
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            
        Returns:
            Optional[Dict[str, Any]]: Данные аутентификации или None
        """
        user = await self.user_service.authenticate_user(email, password)
        if not user:
            return None
        
        # Создание токенов
        access_token = create_access_token(
            subject=str(user.id),
            secret=settings.jwt_secret,
            minutes=settings.jwt_access_token_expire_minutes
        )
        
        refresh_token = create_refresh_token(
            subject=str(user.id),
            secret=settings.jwt_secret,
            minutes=settings.jwt_access_token_expire_minutes * 24 * 7  # 7 дней
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_access_token_expire_minutes * 60,
            "user": user.to_dict()
        }
    
    async def register(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Регистрация нового пользователя.
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            first_name: Имя пользователя
            last_name: Фамилия пользователя
            
        Returns:
            Dict[str, Any]: Данные зарегистрированного пользователя
            
        Raises:
            ValueError: Если пользователь с таким email уже существует
        """
        user = await self.user_service.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        return {
            "user": user.to_dict(),
            "verification_token": user.verification_token,
            "message": "Пользователь успешно зарегистрирован. Проверьте email для верификации."
        }
    
    async def verify_email(self, verification_token: str) -> bool:
        """
        Верификация email пользователя.
        
        Args:
            verification_token: Токен верификации
            
        Returns:
            bool: True если верификация успешна, False иначе
        """
        return await self.user_service.verify_user(verification_token)
    
    async def initiate_password_reset(self, email: str) -> bool:
        """
        Инициация восстановления пароля.
        
        Args:
            email: Email пользователя
            
        Returns:
            bool: True если пользователь найден, False иначе
        """
        return await self.user_service.initiate_password_reset(email)
    
    async def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Сброс пароля по токену.
        
        Args:
            reset_token: Токен восстановления
            new_password: Новый пароль
            
        Returns:
            bool: True если сброс успешен, False иначе
        """
        return await self.user_service.reset_password(reset_token, new_password)
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Обновление access токена.
        
        Args:
            refresh_token: Refresh токен
            
        Returns:
            Optional[Dict[str, Any]]: Новые токены или None
        """
        # TODO: Реализовать проверку refresh токена
        # Пока что возвращаем заглушку
        return None
    
    async def get_current_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение текущего пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Dict[str, Any]]: Данные пользователя или None
        """
        user = await self.user_service.get_user_by_id(user_id)
        if not user:
            return None
        
        return user.to_dict()
    
    async def update_profile(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Обновление профиля пользователя.
        
        Args:
            user_id: ID пользователя
            first_name: Новое имя
            last_name: Новая фамилия
            
        Returns:
            Optional[Dict[str, Any]]: Обновленные данные пользователя или None
        """
        user = await self.user_service.update_user_profile(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name
        )
        
        if not user:
            return None
        
        return user.to_dict()
    
    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Изменение пароля пользователя.
        
        Args:
            user_id: ID пользователя
            old_password: Старый пароль
            new_password: Новый пароль
            
        Returns:
            bool: True если изменение успешно, False иначе
        """
        return await self.user_service.change_password(user_id, old_password, new_password)
