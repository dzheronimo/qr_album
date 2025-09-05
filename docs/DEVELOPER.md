# 👨‍💻 Руководство разработчика QR-Albums

## 📋 Содержание

1. [Настройка среды разработки](#настройка-среды-разработки)
2. [Структура проекта](#структура-проекта)
3. [Стандарты кодирования](#стандарты-кодирования)
4. [Работа с API](#работа-с-api)
5. [Тестирование](#тестирование)
6. [Добавление новых функций](#добавление-новых-функций)
7. [Отладка](#отладка)
8. [Производительность](#производительность)
9. [Безопасность](#безопасность)
10. [Полезные инструменты](#полезные-инструменты)

## 🛠️ Настройка среды разработки

### Предварительные требования

- **Python**: 3.11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+
- **IDE**: VS Code, PyCharm, или любой другой с поддержкой Python

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/dzheronimo/qr_album.git
cd qr_album

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
pip install -r tests/requirements.txt
pip install -r requirements-dev.txt

# Настройка pre-commit hooks
pre-commit install
```

### Настройка IDE

#### VS Code

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "python.testing.unittestEnabled": false
}
```

#### PyCharm

1. Откройте проект в PyCharm
2. Настройте интерпретатор Python на `venv/bin/python`
3. Включите поддержку pytest
4. Настройте форматирование кода с Black

### Переменные окружения

```bash
# Копирование файла окружения
cp .env.example .env

# Редактирование для разработки
nano .env
```

**Рекомендуемые настройки для разработки**:

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Локальные базы данных
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=qr_albums_dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=dev_password

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=dev_redis_password

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Тестовые ключи
JWT_SECRET_KEY=dev_jwt_secret_key
OPENAI_API_KEY=your_test_openai_key
```

## 📁 Структура проекта

```
qr_album/
├── apps/                          # Микросервисы
│   ├── auth-svc/                 # Сервис аутентификации
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py           # Точка входа FastAPI
│   │   │   ├── config.py         # Конфигурация
│   │   │   ├── database.py       # Настройка БД
│   │   │   ├── models/           # SQLAlchemy модели
│   │   │   ├── schemas/          # Pydantic схемы
│   │   │   ├── services/         # Бизнес-логика
│   │   │   ├── routes/           # API эндпоинты
│   │   │   └── integration/      # Интеграция с другими сервисами
│   │   ├── alembic/              # Миграции БД
│   │   ├── tests/                # Тесты сервиса
│   │   ├── requirements.txt      # Зависимости
│   │   ├── Dockerfile           # Docker образ
│   │   └── README.md            # Документация сервиса
│   └── ...                       # Другие сервисы
├── packages/                      # Общие пакеты
│   └── py-commons/               # Общие утилиты
│       ├── __init__.py
│       ├── auth/                 # Аутентификация
│       ├── database/             # Работа с БД
│       ├── integration/          # Интеграция
│       └── utils/                # Утилиты
├── tests/                         # Тесты
│   ├── unit/                     # Unit тесты
│   ├── integration/              # Integration тесты
│   ├── e2e/                      # E2E тесты
│   ├── conftest.py              # Общие фикстуры
│   └── requirements.txt         # Зависимости для тестов
├── docs/                          # Документация
├── docker-compose.yml            # Docker Compose
├── docker-compose.dev.yml        # Docker Compose для разработки
├── Makefile                      # Команды для разработки
├── pytest.ini                   # Конфигурация pytest
└── README.md                     # Основная документация
```

### Структура микросервиса

Каждый микросервис следует единой структуре:

```
service-name/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI приложение
│   ├── config.py                 # Конфигурация
│   ├── database.py               # Настройка БД
│   ├── models/                   # SQLAlchemy модели
│   │   ├── __init__.py
│   │   └── model_name.py
│   ├── schemas/                  # Pydantic схемы
│   │   ├── __init__.py
│   │   └── schema_name.py
│   ├── services/                 # Бизнес-логика
│   │   ├── __init__.py
│   │   └── service_name.py
│   ├── routes/                   # API эндпоинты
│   │   ├── __init__.py
│   │   └── route_name.py
│   └── integration/              # Интеграция
│       ├── __init__.py
│       ├── event_handlers.py
│       ├── service_clients.py
│       └── cache_manager.py
├── alembic/                      # Миграции
├── tests/                        # Тесты
├── requirements.txt              # Зависимости
├── Dockerfile                   # Docker образ
├── env.example                  # Пример переменных окружения
└── README.md                    # Документация
```

## 📝 Стандарты кодирования

### Python Style Guide

Мы следуем **PEP 8** с некоторыми дополнениями:

```python
# Импорты
import os
import sys
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse

# Константы
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

# Классы
class UserService:
    """Сервис для работы с пользователями."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Создание нового пользователя.
        
        Args:
            user_data: Данные для создания пользователя
            
        Returns:
            User: Созданный пользователь
            
        Raises:
            ValueError: Если пользователь уже существует
        """
        # Проверка существования пользователя
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ValueError("User already exists")
        
        # Создание пользователя
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=self._hash_password(user_data.password)
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля."""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Функции
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя из токена."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Type Hints

Всегда используйте type hints:

```python
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

def process_users(
    users: List[User],
    filter_active: bool = True,
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """Обработка списка пользователей."""
    pass

async def get_user_by_id(user_id: int) -> Optional[User]:
    """Получение пользователя по ID."""
    pass
```

### Docstrings

Используйте Google style docstrings:

```python
def create_album(
    album_data: AlbumCreate,
    user_id: int,
    db: Session
) -> Album:
    """
    Создание нового альбома.
    
    Args:
        album_data: Данные для создания альбома
        user_id: ID пользователя-создателя
        db: Сессия базы данных
        
    Returns:
        Album: Созданный альбом
        
    Raises:
        ValueError: Если пользователь не найден
        HTTPException: Если произошла ошибка при создании
        
    Example:
        >>> album_data = AlbumCreate(title="My Album", description="Test")
        >>> album = create_album(album_data, user_id=1, db=session)
        >>> print(album.title)
        My Album
    """
    pass
```

### Обработка ошибок

```python
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

async def create_user(user_data: UserCreate, db: Session) -> User:
    """Создание пользователя с обработкой ошибок."""
    try:
        user = User(**user_data.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

## 🔌 Работа с API

### Создание эндпоинтов

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.services import UserService
from app.auth import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Создание нового пользователя.
    
    - **email**: Email пользователя (должен быть уникальным)
    - **username**: Имя пользователя
    - **password**: Пароль (минимум 8 символов)
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о текущем пользователе."""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение пользователя по ID."""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
```

### Валидация данных

```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
import re

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePass123",
                "first_name": "John",
                "last_name": "Doe"
            }
        }
```

### Middleware

```python
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Логирование входящего запроса
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host}"
        )
        
        # Обработка запроса
        response = await call_next(request)
        
        # Логирование ответа
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} "
            f"in {process_time:.3f}s"
        )
        
        # Добавление заголовка времени обработки
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

# Регистрация middleware
app.add_middleware(LoggingMiddleware)
```

## 🧪 Тестирование

### Unit тесты

```python
import pytest
from unittest.mock import Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import UserService
from app.schemas import UserCreate
from app.models import User

class TestUserService:
    """Тесты для UserService."""
    
    @pytest.fixture
    async def user_service(self, test_db_session: AsyncSession):
        """Фикстура для UserService."""
        return UserService(test_db_session)
    
    @pytest.mark.unit
    async def test_create_user_success(self, user_service: UserService):
        """Тест успешного создания пользователя."""
        user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        with patch.object(user_service, '_hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            user = await user_service.create_user(user_data)
            
            assert user.email == "test@example.com"
            assert user.username == "testuser"
            assert user.hashed_password == "hashed_password"
            mock_hash.assert_called_once_with("password123")
    
    @pytest.mark.unit
    async def test_create_user_duplicate_email(self, user_service: UserService):
        """Тест создания пользователя с дублирующимся email."""
        # Создаем первого пользователя
        user_data1 = UserCreate(
            email="test@example.com",
            username="user1",
            password="password123"
        )
        
        await user_service.create_user(user_data1)
        
        # Пытаемся создать второго пользователя с тем же email
        user_data2 = UserCreate(
            email="test@example.com",
            username="user2",
            password="password123"
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            await user_service.create_user(user_data2)
```

### Integration тесты

```python
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app

class TestUserIntegration:
    """Integration тесты для пользователей."""
    
    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента."""
        return TestClient(app)
    
    @pytest.mark.integration
    def test_user_registration_flow(self, client: TestClient):
        """Тест полного потока регистрации пользователя."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        
        user = response.json()
        assert user["email"] == user_data["email"]
        assert user["username"] == user_data["username"]
        assert "id" in user
    
    @pytest.mark.integration
    def test_user_login_flow(self, client: TestClient):
        """Тест полного потока входа пользователя."""
        # Сначала регистрируем пользователя
        user_data = {
            "email": "loginuser@example.com",
            "username": "loginuser",
            "password": "password123"
        }
        
        client.post("/api/v1/users/", json=user_data)
        
        # Теперь входим
        login_data = {
            "email": "loginuser@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        token_data = response.json()
        assert "access_token" in token_data
        assert "refresh_token" in token_data
```

### E2E тесты

```python
import pytest
from httpx import AsyncClient

class TestFullWorkflow:
    """E2E тесты для полного рабочего процесса."""
    
    @pytest.mark.e2e
    @pytest.mark.slow
    async def test_complete_album_creation_workflow(self, client: AsyncClient):
        """Тест полного процесса создания альбома с QR кодами."""
        
        # 1. Регистрация пользователя
        user_data = {
            "email": "e2e@example.com",
            "username": "e2euser",
            "password": "password123"
        }
        
        response = await client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["id"]
        
        # 2. Вход пользователя
        login_data = {
            "email": "e2e@example.com",
            "password": "password123"
        }
        
        response = await client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # 3. Создание альбома
        album_data = {
            "title": "E2E Test Album",
            "description": "Album created during E2E testing",
            "is_public": True
        }
        
        response = await client.post("/api/v1/albums/", json=album_data, headers=headers)
        assert response.status_code == 201
        album_id = response.json()["id"]
        
        # 4. Создание страницы
        page_data = {
            "title": "Test Page",
            "content": "Test content",
            "page_number": 1
        }
        
        response = await client.post(
            f"/api/v1/albums/{album_id}/pages/",
            json=page_data,
            headers=headers
        )
        assert response.status_code == 201
        page_id = response.json()["id"]
        
        # 5. Генерация QR кода
        qr_data = {
            "page_id": page_id,
            "album_id": album_id
        }
        
        response = await client.post("/api/v1/qr/generate", json=qr_data, headers=headers)
        assert response.status_code == 201
        qr_code = response.json()
        
        assert "id" in qr_code
        assert "url" in qr_code
```

### Запуск тестов

```bash
# Все тесты
make test

# Только unit тесты
make test-unit

# Только integration тесты
make test-integration

# E2E тесты
make test-e2e

# Тесты с покрытием
make test-coverage

# Быстрые тесты
make test-fast

# Параллельное выполнение
make test-parallel
```

## 🚀 Добавление новых функций

### 1. Создание нового сервиса

```bash
# Создание структуры сервиса
mkdir -p apps/new-service/app/{models,schemas,services,routes,integration}
mkdir -p apps/new-service/alembic/versions
mkdir -p apps/new-service/tests

# Создание основных файлов
touch apps/new-service/app/__init__.py
touch apps/new-service/app/main.py
touch apps/new-service/app/config.py
touch apps/new-service/app/database.py
touch apps/new-service/requirements.txt
touch apps/new-service/Dockerfile
touch apps/new-service/README.md
```

### 2. Настройка FastAPI приложения

```python
# apps/new-service/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routes import router

app = FastAPI(
    title="New Service",
    description="Description of new service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """События при запуске."""
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """События при остановке."""
    pass

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "new-service"}
```

### 3. Создание моделей

```python
# apps/new-service/app/models/entity.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Entity(Base):
    """Модель сущности."""
    
    __tablename__ = "entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}')>"
```

### 4. Создание схем

```python
# apps/new-service/app/schemas/entity.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class EntityBase(BaseModel):
    """Базовая схема сущности."""
    name: str
    description: Optional[str] = None
    is_active: bool = True
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v

class EntityCreate(EntityBase):
    """Схема для создания сущности."""
    pass

class EntityUpdate(BaseModel):
    """Схема для обновления сущности."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class EntityResponse(EntityBase):
    """Схема ответа с сущностью."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### 5. Создание сервиса

```python
# apps/new-service/app/services/entity_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.entity import Entity
from app.schemas.entity import EntityCreate, EntityUpdate

class EntityService:
    """Сервис для работы с сущностями."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_entity(self, entity_data: EntityCreate) -> Entity:
        """Создание новой сущности."""
        entity = Entity(**entity_data.dict())
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    async def get_entity_by_id(self, entity_id: int) -> Optional[Entity]:
        """Получение сущности по ID."""
        return self.db.query(Entity).filter(Entity.id == entity_id).first()
    
    async def get_entities(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Entity]:
        """Получение списка сущностей."""
        query = self.db.query(Entity)
        
        if is_active is not None:
            query = query.filter(Entity.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    async def update_entity(
        self, 
        entity_id: int, 
        entity_data: EntityUpdate
    ) -> Optional[Entity]:
        """Обновление сущности."""
        entity = await self.get_entity_by_id(entity_id)
        if not entity:
            return None
        
        update_data = entity_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    async def delete_entity(self, entity_id: int) -> bool:
        """Удаление сущности."""
        entity = await self.get_entity_by_id(entity_id)
        if not entity:
            return False
        
        self.db.delete(entity)
        self.db.commit()
        return True
```

### 6. Создание роутеров

```python
# apps/new-service/app/routes/entity.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.entity import Entity
from app.schemas.entity import EntityCreate, EntityUpdate, EntityResponse
from app.services.entity_service import EntityService

router = APIRouter(prefix="/entities", tags=["entities"])

@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: EntityCreate,
    db: Session = Depends(get_db)
):
    """Создание новой сущности."""
    entity_service = EntityService(db)
    entity = await entity_service.create_entity(entity_data)
    return entity

@router.get("/", response_model=List[EntityResponse])
async def get_entities(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Получение списка сущностей."""
    entity_service = EntityService(db)
    entities = await entity_service.get_entities(skip, limit, is_active)
    return entities

@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """Получение сущности по ID."""
    entity_service = EntityService(db)
    entity = await entity_service.get_entity_by_id(entity_id)
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    return entity

@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: int,
    entity_data: EntityUpdate,
    db: Session = Depends(get_db)
):
    """Обновление сущности."""
    entity_service = EntityService(db)
    entity = await entity_service.update_entity(entity_id, entity_data)
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
    
    return entity

@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: int,
    db: Session = Depends(get_db)
):
    """Удаление сущности."""
    entity_service = EntityService(db)
    success = await entity_service.delete_entity(entity_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found"
        )
```

### 7. Создание миграций

```bash
# Создание миграции
cd apps/new-service
alembic revision --autogenerate -m "Create entities table"

# Применение миграции
alembic upgrade head
```

### 8. Добавление тестов

```python
# apps/new-service/tests/test_entity_service.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.entity_service import EntityService
from app.schemas.entity import EntityCreate

class TestEntityService:
    """Тесты для EntityService."""
    
    @pytest.fixture
    async def entity_service(self, test_db_session: AsyncSession):
        """Фикстура для EntityService."""
        return EntityService(test_db_session)
    
    @pytest.mark.unit
    async def test_create_entity_success(self, entity_service: EntityService):
        """Тест успешного создания сущности."""
        entity_data = EntityCreate(
            name="Test Entity",
            description="Test description"
        )
        
        entity = await entity_service.create_entity(entity_data)
        
        assert entity.name == "Test Entity"
        assert entity.description == "Test description"
        assert entity.is_active is True
        assert entity.id is not None
```

## 🐛 Отладка

### Логирование

```python
import logging
from app.config import settings

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Использование в коде
logger.info("User created successfully", extra={"user_id": user.id})
logger.error("Database connection failed", exc_info=True)
logger.debug("Processing request", extra={"request_id": request_id})
```

### Отладка в IDE

#### VS Code

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/apps/auth-svc/app/main.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

#### PyCharm

1. Создайте конфигурацию запуска
2. Укажите путь к main.py
3. Установите переменные окружения
4. Запустите в режиме отладки

### Отладка в Docker

```bash
# Запуск с отладочными логами
docker-compose up --build

# Подключение к контейнеру
docker-compose exec auth-svc bash

# Просмотр логов
docker-compose logs -f auth-svc

# Отладка с pdb
docker-compose exec auth-svc python -m pdb app/main.py
```

### Профилирование

```python
import cProfile
import pstats
from io import StringIO

def profile_function(func):
    """Декоратор для профилирования функций."""
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        result = func(*args, **kwargs)
        
        pr.disable()
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        logger.info(f"Profile for {func.__name__}:\n{s.getvalue()}")
        return result
    
    return wrapper

# Использование
@profile_function
async def slow_function():
    # Ваш код
    pass
```

## ⚡ Производительность

### Оптимизация запросов к БД

```python
# Плохо - N+1 проблема
users = db.query(User).all()
for user in users:
    print(user.profile.name)  # Дополнительный запрос для каждого пользователя

# Хорошо - eager loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.profile)).all()
for user in users:
    print(user.profile.name)  # Нет дополнительных запросов
```

### Кэширование

```python
from functools import lru_cache
import redis
from app.config import settings

# In-memory кэширование
@lru_cache(maxsize=128)
def expensive_calculation(param):
    # Дорогие вычисления
    return result

# Redis кэширование
redis_client = redis.Redis.from_url(settings.REDIS_URL)

async def get_cached_data(key: str):
    """Получение данных из кэша."""
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Получение данных из БД
    data = await get_data_from_db()
    
    # Сохранение в кэш
    redis_client.setex(key, 3600, json.dumps(data))
    return data
```

### Асинхронность

```python
import asyncio
from typing import List

async def process_items_parallel(items: List[str]) -> List[str]:
    """Параллельная обработка элементов."""
    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)
    return results

async def process_item(item: str) -> str:
    """Обработка одного элемента."""
    # Асинхронная операция
    await asyncio.sleep(0.1)
    return f"processed_{item}"
```

## 🔒 Безопасность

### Валидация входных данных

```python
from pydantic import BaseModel, validator
import re

class UserCreate(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password too short')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain digit')
        return v
```

### Защита от SQL инъекций

```python
# Плохо - уязвимо к SQL инъекциям
user_id = "1; DROP TABLE users;"
query = f"SELECT * FROM users WHERE id = {user_id}"

# Хорошо - использование ORM
user = db.query(User).filter(User.id == user_id).first()

# Или параметризованные запросы
query = "SELECT * FROM users WHERE id = :user_id"
result = db.execute(query, {"user_id": user_id})
```

### Аутентификация и авторизация

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Получение текущего пользователя из JWT токена."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user
    
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

## 🛠️ Полезные инструменты

### Pre-commit hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

### Makefile команды

```makefile
# Форматирование кода
format:
	black apps/ packages/ tests/
	isort apps/ packages/ tests/

# Линтинг
lint:
	flake8 apps/ packages/ tests/
	black --check apps/ packages/ tests/
	isort --check-only apps/ packages/ tests/
	mypy apps/ packages/

# Тестирование
test:
	pytest tests/ -v

# Очистка
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
```

### Docker команды

```bash
# Сборка образа
docker build -t qr-albums/auth-svc:latest apps/auth-svc/

# Запуск контейнера
docker run -p 8001:8001 qr-albums/auth-svc:latest

# Просмотр логов
docker logs -f container_id

# Подключение к контейнеру
docker exec -it container_id bash
```

### Полезные скрипты

```bash
#!/bin/bash
# scripts/setup_dev.sh

echo "Setting up development environment..."

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install -r tests/requirements.txt
pip install -r requirements-dev.txt

# Настройка pre-commit
pre-commit install

# Копирование файла окружения
cp .env.example .env

echo "Development environment setup complete!"
echo "Don't forget to edit .env file with your settings."
```

---

*Руководство обновлено: 2024-01-01*
