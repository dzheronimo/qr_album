"""
Сервис для работы с настройками пользователей.

Содержит бизнес-логику для CRUD операций с настройками.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from app.models.user_profile import UserSettings, ThemeType, LanguageType


class SettingsService:
    """Сервис для работы с настройками пользователей."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_default_settings(self, user_id: int) -> UserSettings:
        """
        Создание настроек по умолчанию для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserSettings: Созданные настройки
        """
        settings = UserSettings(user_id=user_id)
        
        try:
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
            return settings
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Настройки для данного пользователя уже существуют")
    
    async def get_settings_by_user_id(self, user_id: int) -> Optional[UserSettings]:
        """
        Получение настроек по ID пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[UserSettings]: Настройки или None
        """
        result = await self.db.execute(
            select(UserSettings).where(UserSettings.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_settings(self, user_id: int) -> UserSettings:
        """
        Получение настроек или создание по умолчанию.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserSettings: Настройки пользователя
        """
        settings = await self.get_settings_by_user_id(user_id)
        if not settings:
            settings = await self.create_default_settings(user_id)
        return settings
    
    async def update_settings(
        self,
        user_id: int,
        theme: Optional[ThemeType] = None,
        language: Optional[LanguageType] = None,
        email_notifications: Optional[bool] = None,
        push_notifications: Optional[bool] = None,
        sms_notifications: Optional[bool] = None,
        profile_visibility: Optional[str] = None,
        album_visibility: Optional[str] = None,
        allow_following: Optional[bool] = None,
        two_factor_enabled: Optional[bool] = None,
        login_notifications: Optional[bool] = None,
        auto_save_drafts: Optional[bool] = None,
        compress_images: Optional[bool] = None,
        max_file_size_mb: Optional[int] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Optional[UserSettings]:
        """
        Обновление настроек пользователя.
        
        Args:
            user_id: ID пользователя
            theme: Тема оформления
            language: Язык интерфейса
            email_notifications: Email уведомления
            push_notifications: Push уведомления
            sms_notifications: SMS уведомления
            profile_visibility: Видимость профиля
            album_visibility: Видимость альбомов
            allow_following: Разрешить подписки
            two_factor_enabled: Двухфакторная аутентификация
            login_notifications: Уведомления о входе
            auto_save_drafts: Автосохранение черновиков
            compress_images: Сжатие изображений
            max_file_size_mb: Максимальный размер файла
            custom_settings: Пользовательские настройки
            
        Returns:
            Optional[UserSettings]: Обновленные настройки или None
        """
        settings = await self.get_or_create_settings(user_id)
        
        # Обновляем поля
        update_data = {}
        
        if theme is not None:
            update_data["theme"] = theme
        if language is not None:
            update_data["language"] = language
        if email_notifications is not None:
            update_data["email_notifications"] = email_notifications
        if push_notifications is not None:
            update_data["push_notifications"] = push_notifications
        if sms_notifications is not None:
            update_data["sms_notifications"] = sms_notifications
        if profile_visibility is not None:
            update_data["profile_visibility"] = profile_visibility
        if album_visibility is not None:
            update_data["album_visibility"] = album_visibility
        if allow_following is not None:
            update_data["allow_following"] = allow_following
        if two_factor_enabled is not None:
            update_data["two_factor_enabled"] = two_factor_enabled
        if login_notifications is not None:
            update_data["login_notifications"] = login_notifications
        if auto_save_drafts is not None:
            update_data["auto_save_drafts"] = auto_save_drafts
        if compress_images is not None:
            update_data["compress_images"] = compress_images
        if max_file_size_mb is not None:
            update_data["max_file_size_mb"] = max_file_size_mb
        if custom_settings is not None:
            update_data["custom_settings"] = custom_settings
        
        if not update_data:
            return settings
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_settings_by_user_id(user_id)
    
    async def update_custom_setting(
        self,
        user_id: int,
        key: str,
        value: Any
    ) -> Optional[UserSettings]:
        """
        Обновление пользовательской настройки.
        
        Args:
            user_id: ID пользователя
            key: Ключ настройки
            value: Значение настройки
            
        Returns:
            Optional[UserSettings]: Обновленные настройки или None
        """
        settings = await self.get_or_create_settings(user_id)
        
        custom_settings = settings.custom_settings or {}
        custom_settings[key] = value
        
        return await self.update_settings(
            user_id=user_id,
            custom_settings=custom_settings
        )
    
    async def get_custom_setting(
        self,
        user_id: int,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Получение пользовательской настройки.
        
        Args:
            user_id: ID пользователя
            key: Ключ настройки
            default: Значение по умолчанию
            
        Returns:
            Any: Значение настройки или значение по умолчанию
        """
        settings = await self.get_settings_by_user_id(user_id)
        if not settings or not settings.custom_settings:
            return default
        
        return settings.custom_settings.get(key, default)
    
    async def delete_custom_setting(
        self,
        user_id: int,
        key: str
    ) -> Optional[UserSettings]:
        """
        Удаление пользовательской настройки.
        
        Args:
            user_id: ID пользователя
            key: Ключ настройки
            
        Returns:
            Optional[UserSettings]: Обновленные настройки или None
        """
        settings = await self.get_settings_by_user_id(user_id)
        if not settings or not settings.custom_settings:
            return settings
        
        custom_settings = settings.custom_settings.copy()
        if key in custom_settings:
            del custom_settings[key]
        
        return await self.update_settings(
            user_id=user_id,
            custom_settings=custom_settings
        )
    
    async def delete_settings(self, user_id: int) -> bool:
        """
        Удаление настроек пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        settings = await self.get_settings_by_user_id(user_id)
        if not settings:
            return False
        
        await self.db.execute(
            delete(UserSettings).where(UserSettings.user_id == user_id)
        )
        await self.db.commit()
        
        return True
    
    async def reset_to_defaults(self, user_id: int) -> Optional[UserSettings]:
        """
        Сброс настроек к значениям по умолчанию.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[UserSettings]: Сброшенные настройки или None
        """
        settings = await self.get_settings_by_user_id(user_id)
        if not settings:
            return None
        
        # Создаем новые настройки по умолчанию
        default_settings = UserSettings(user_id=user_id)
        
        await self.db.execute(
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(
                theme=default_settings.theme,
                language=default_settings.language,
                email_notifications=default_settings.email_notifications,
                push_notifications=default_settings.push_notifications,
                sms_notifications=default_settings.sms_notifications,
                profile_visibility=default_settings.profile_visibility,
                album_visibility=default_settings.album_visibility,
                allow_following=default_settings.allow_following,
                two_factor_enabled=default_settings.two_factor_enabled,
                login_notifications=default_settings.login_notifications,
                auto_save_drafts=default_settings.auto_save_drafts,
                compress_images=default_settings.compress_images,
                max_file_size_mb=default_settings.max_file_size_mb,
                custom_settings=None,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return await self.get_settings_by_user_id(user_id)
