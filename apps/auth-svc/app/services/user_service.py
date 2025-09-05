"""
Сервис для работы с пользователями.

Содержит бизнес-логику для CRUD операций с пользователями.
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.utils.password import get_password_hash, verify_password
from app.utils.tokens import generate_verification_token, generate_reset_token, get_token_expiry


class UserService:
    """Сервис для работы с пользователями."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_user(
        self,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Создание нового пользователя.
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            first_name: Имя пользователя
            last_name: Фамилия пользователя
            
        Returns:
            User: Созданный пользователь
            
        Raises:
            ValueError: Если пользователь с таким email уже существует
        """
        # Проверка существования пользователя
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")
        
        # Хеширование пароля
        hashed_password = get_password_hash(password)
        
        # Генерация токена верификации
        verification_token = generate_verification_token()
        verification_expires = get_token_expiry(minutes=24 * 60)  # 24 часа
        
        # Создание пользователя
        user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            verification_token=verification_token,
            verification_token_expires=verification_expires
        )
        
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Пользователь с таким email уже существует")
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получение пользователя по email.
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Аутентификация пользователя.
        
        Args:
            email: Email пользователя
            password: Пароль пользователя
            
        Returns:
            Optional[User]: Пользователь если аутентификация успешна, None иначе
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Обновление времени последнего входа
        await self.update_last_login(user.id)
        
        return user
    
    async def update_last_login(self, user_id: int) -> None:
        """
        Обновление времени последнего входа.
        
        Args:
            user_id: ID пользователя
        """
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await self.db.commit()
    
    async def verify_user(self, verification_token: str) -> bool:
        """
        Верификация пользователя по токену.
        
        Args:
            verification_token: Токен верификации
            
        Returns:
            bool: True если верификация успешна, False иначе
        """
        result = await self.db.execute(
            select(User).where(User.verification_token == verification_token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        if user.verification_token_expires and datetime.utcnow() > user.verification_token_expires:
            return False
        
        # Обновление статуса верификации
        await self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                is_verified=True,
                verification_token=None,
                verification_token_expires=None
            )
        )
        await self.db.commit()
        
        return True
    
    async def initiate_password_reset(self, email: str) -> bool:
        """
        Инициация восстановления пароля.
        
        Args:
            email: Email пользователя
            
        Returns:
            bool: True если пользователь найден, False иначе
        """
        user = await self.get_user_by_email(email)
        if not user:
            return False
        
        # Генерация токена восстановления
        reset_token = generate_reset_token()
        reset_expires = get_token_expiry(minutes=60)  # 1 час
        
        # Обновление токена восстановления
        await self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                reset_token=reset_token,
                reset_token_expires=reset_expires
            )
        )
        await self.db.commit()
        
        return True
    
    async def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Сброс пароля по токену.
        
        Args:
            reset_token: Токен восстановления
            new_password: Новый пароль
            
        Returns:
            bool: True если сброс успешен, False иначе
        """
        result = await self.db.execute(
            select(User).where(User.reset_token == reset_token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        if user.reset_token_expires and datetime.utcnow() > user.reset_token_expires:
            return False
        
        # Хеширование нового пароля
        hashed_password = get_password_hash(new_password)
        
        # Обновление пароля
        await self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                hashed_password=hashed_password,
                reset_token=None,
                reset_token_expires=None
            )
        )
        await self.db.commit()
        
        return True
    
    async def update_user_profile(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Optional[User]:
        """
        Обновление профиля пользователя.
        
        Args:
            user_id: ID пользователя
            first_name: Новое имя
            last_name: Новая фамилия
            
        Returns:
            Optional[User]: Обновленный пользователь или None
        """
        update_data = {}
        
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        
        if not update_data:
            return await self.get_user_by_id(user_id)
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_user_by_id(user_id)
    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Изменение пароля пользователя.
        
        Args:
            user_id: ID пользователя
            old_password: Старый пароль
            new_password: Новый пароль
            
        Returns:
            bool: True если изменение успешно, False иначе
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(old_password, user.hashed_password):
            return False
        
        # Хеширование нового пароля
        hashed_password = get_password_hash(new_password)
        
        # Обновление пароля
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                hashed_password=hashed_password,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Деактивация пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если деактивация успешна, False иначе
        """
        result = await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        
        return result.rowcount > 0
