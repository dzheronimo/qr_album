"""
Сервис для работы с профилями пользователей.

Содержит бизнес-логику для CRUD операций с профилями.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError

from app.models.user_profile import UserProfile


class ProfileService:
    """Сервис для работы с профилями пользователей."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_profile(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        location: Optional[str] = None,
        timezone: Optional[str] = None,
        avatar_url: Optional[str] = None,
        cover_image_url: Optional[str] = None,
        social_links: Optional[Dict[str, Any]] = None,
        is_public: bool = True,
        show_email: bool = False,
        show_phone: bool = False,
        show_location: bool = False,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """
        Создание профиля пользователя.
        
        Args:
            user_id: ID пользователя
            first_name: Имя
            last_name: Фамилия
            middle_name: Отчество
            display_name: Отображаемое имя
            bio: Биография
            phone: Телефон
            website: Веб-сайт
            location: Местоположение
            timezone: Часовой пояс
            avatar_url: URL аватара
            cover_image_url: URL обложки
            social_links: Ссылки на социальные сети
            is_public: Публичный профиль
            show_email: Показывать email
            show_phone: Показывать телефон
            show_location: Показывать местоположение
            metadata: Дополнительные метаданные
            
        Returns:
            UserProfile: Созданный профиль
            
        Raises:
            ValueError: Если профиль уже существует
        """
        profile = UserProfile(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            display_name=display_name,
            bio=bio,
            phone=phone,
            website=website,
            location=location,
            timezone=timezone,
            avatar_url=avatar_url,
            cover_image_url=cover_image_url,
            social_links=social_links,
            is_public=is_public,
            show_email=show_email,
            show_phone=show_phone,
            show_location=show_location,
            extra_data=extra_data
        )
        
        try:
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)
            return profile
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Профиль для данного пользователя уже существует")
    
    async def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """
        Получение профиля по ID пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[UserProfile]: Профиль или None
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_profile_by_id(self, profile_id: int) -> Optional[UserProfile]:
        """
        Получение профиля по ID.
        
        Args:
            profile_id: ID профиля
            
        Returns:
            Optional[UserProfile]: Профиль или None
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.id == profile_id)
        )
        return result.scalar_one_or_none()
    
    async def get_public_profiles(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None
    ) -> List[UserProfile]:
        """
        Получение публичных профилей.
        
        Args:
            skip: Количество пропускаемых записей
            limit: Лимит записей
            search: Поисковый запрос
            
        Returns:
            List[UserProfile]: Список публичных профилей
        """
        query = select(UserProfile).where(UserProfile.is_public == True)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (UserProfile.display_name.ilike(search_filter)) |
                (UserProfile.first_name.ilike(search_filter)) |
                (UserProfile.last_name.ilike(search_filter)) |
                (UserProfile.bio.ilike(search_filter))
            )
        
        query = query.offset(skip).limit(limit).order_by(UserProfile.updated_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_profile(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        location: Optional[str] = None,
        timezone: Optional[str] = None,
        avatar_url: Optional[str] = None,
        cover_image_url: Optional[str] = None,
        social_links: Optional[Dict[str, Any]] = None,
        is_public: Optional[bool] = None,
        show_email: Optional[bool] = None,
        show_phone: Optional[bool] = None,
        show_location: Optional[bool] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[UserProfile]:
        """
        Обновление профиля пользователя.
        
        Args:
            user_id: ID пользователя
            first_name: Имя
            last_name: Фамилия
            middle_name: Отчество
            display_name: Отображаемое имя
            bio: Биография
            phone: Телефон
            website: Веб-сайт
            location: Местоположение
            timezone: Часовой пояс
            avatar_url: URL аватара
            cover_image_url: URL обложки
            social_links: Ссылки на социальные сети
            is_public: Публичный профиль
            show_email: Показывать email
            show_phone: Показывать телефон
            show_location: Показывать местоположение
            metadata: Дополнительные метаданные
            
        Returns:
            Optional[UserProfile]: Обновленный профиль или None
        """
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        if middle_name is not None:
            update_data["middle_name"] = middle_name
        if display_name is not None:
            update_data["display_name"] = display_name
        if bio is not None:
            update_data["bio"] = bio
        if phone is not None:
            update_data["phone"] = phone
        if website is not None:
            update_data["website"] = website
        if location is not None:
            update_data["location"] = location
        if timezone is not None:
            update_data["timezone"] = timezone
        if avatar_url is not None:
            update_data["avatar_url"] = avatar_url
        if cover_image_url is not None:
            update_data["cover_image_url"] = cover_image_url
        if social_links is not None:
            update_data["social_links"] = social_links
        if is_public is not None:
            update_data["is_public"] = is_public
        if show_email is not None:
            update_data["show_email"] = show_email
        if show_phone is not None:
            update_data["show_phone"] = show_phone
        if show_location is not None:
            update_data["show_location"] = show_location
        if extra_data is not None:
            update_data["extra_data"] = extra_data
        
        if not update_data:
            return profile
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(UserProfile)
            .where(UserProfile.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_profile_by_user_id(user_id)
    
    async def delete_profile(self, user_id: int) -> bool:
        """
        Удаление профиля пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return False
        
        await self.db.execute(
            delete(UserProfile).where(UserProfile.user_id == user_id)
        )
        await self.db.commit()
        
        return True
    
    async def update_last_seen(self, user_id: int) -> bool:
        """
        Обновление времени последнего посещения.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если обновление успешно, False иначе
        """
        result = await self.db.execute(
            update(UserProfile)
            .where(UserProfile.user_id == user_id)
            .values(last_seen_at=datetime.utcnow())
        )
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def get_profile_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение статистики профиля.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[Dict[str, Any]]: Статистика профиля или None
        """
        profile = await self.get_profile_by_user_id(user_id)
        if not profile:
            return None
        
        # Здесь можно добавить дополнительную статистику
        # например, количество альбомов, медиафайлов и т.д.
        
        return {
            "user_id": user_id,
            "profile_created_at": profile.created_at.isoformat(),
            "last_updated_at": profile.updated_at.isoformat(),
            "last_seen_at": profile.last_seen_at.isoformat() if profile.last_seen_at else None,
            "is_public": profile.is_public,
            "has_avatar": bool(profile.avatar_url),
            "has_cover": bool(profile.cover_image_url),
            "has_bio": bool(profile.bio),
            "has_social_links": bool(profile.social_links),
        }
