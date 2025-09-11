#!/usr/bin/env python3
"""
Скрипт для создания пользователя в auth service.
"""

import asyncio
import sys
from app.database import AsyncSessionLocal
from app.models.user import User
from app.utils.password import get_password_hash
from sqlalchemy import select

async def create_user():
    """Создает пользователя test@example.com с паролем test123."""
    async with AsyncSessionLocal() as db:
        # Проверяем, существует ли пользователь
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Пользователь test@example.com уже существует")
            return
        
        # Создаем хеш пароля
        password_hash = get_password_hash("test123")
        print(f"Хеш пароля: {password_hash}")
        
        # Создаем пользователя
        user = User(
            email="test@example.com",
            hashed_password=password_hash,
            first_name="Test",
            last_name="User",
            is_active=True,
            is_verified=True,
            is_superuser=False
        )
        
        db.add(user)
        await db.commit()
        
        print("Пользователь test@example.com создан успешно")

if __name__ == "__main__":
    asyncio.run(create_user())

