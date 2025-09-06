# 🗄️ Отчет по анализу баз данных и миграций

**Дата**: 2025-09-06  
**Анализируемые сервисы**: Все сервисы с базами данных  

## 🔍 Результаты анализа

### 1. Структура миграций

#### ✅ Настроенные сервисы с Alembic
- **auth-svc**: ✅ Настроен
- **qr-svc**: ✅ Настроен  
- **notification-svc**: ✅ Настроен

#### ❌ Сервисы без миграций
- **album-svc**: ❌ Отсутствует alembic
- **analytics-svc**: ❌ Отсутствует alembic
- **billing-svc**: ❌ Отсутствует alembic
- **media-svc**: ❌ Отсутствует alembic
- **moderation-svc**: ❌ Отсутствует alembic
- **print-svc**: ❌ Отсутствует alembic
- **user-profile-svc**: ❌ Отсутствует alembic

### 2. Проблемы с миграциями

#### ⚠️ Несогласованность конфигурации

**Проблема**: Разные подходы к настройке Alembic

**auth-svc** (синхронный):
```python
from sqlalchemy import engine_from_config
from sqlalchemy import pool

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
```

**qr-svc** (асинхронный):
```python
from sqlalchemy.ext.asyncio import async_engine_from_config

def do_run_migrations(connection: Connection) -> None:
    # Асинхронная конфигурация
```

**notification-svc** (неполная):
```python
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    # Отсутствует context.run_migrations()
```

### 3. Анализ схем баз данных

#### ✅ Хорошо спроектированные модели

**auth-svc - User**:
```python
class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    # ... другие поля
```

**user-profile-svc - UserProfile**:
```python
class UserProfile(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    # ... другие поля
```

#### ✅ Правильные индексы в analytics-svc

```python
# Создание индексов для оптимизации запросов
Index('idx_scan_events_qr_timestamp', ScanEvent.qr_code_id, ScanEvent.scan_timestamp)
Index('idx_scan_events_user_timestamp', ScanEvent.user_id, ScanEvent.scan_timestamp)
Index('idx_user_activities_user_timestamp', UserActivity.user_id, UserActivity.event_timestamp)
Index('idx_page_views_page_timestamp', PageView.page_id, PageView.view_timestamp)
Index('idx_album_views_album_timestamp', AlbumView.album_id, AlbumView.view_timestamp)
```

### 4. Проблемы безопасности

#### ❌ Отсутствие ограничений на длину полей

**Проблема**: Некоторые поля не имеют ограничений на длину

**Примеры**:
```python
# user-profile-svc
bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Без ограничений
website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Слишком длинное

# album-svc  
description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Без ограничений
tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Без ограничений
```

#### ⚠️ Потенциальные проблемы с JSON полями

**Проблема**: JSON поля без валидации схемы

```python
# billing-svc
features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

# user-profile-svc
social_links: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
```

### 5. Проблемы производительности

#### ❌ Отсутствие индексов на внешние ключи

**Проблема**: Не все внешние ключи имеют индексы

**Примеры**:
```python
# album-svc
user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # ✅ Есть индекс

# Но в других моделях могут отсутствовать индексы на FK
```

#### ❌ Отсутствие составных индексов

**Проблема**: Нет составных индексов для частых запросов

**Рекомендации**:
```python
# Для album-svc
Index('idx_albums_user_status', Album.user_id, Album.status)
Index('idx_albums_user_created', Album.user_id, Album.created_at)

# Для billing-svc
Index('idx_subscriptions_user_active', Subscription.user_id, Subscription.is_active)
Index('idx_transactions_user_date', Transaction.user_id, Transaction.created_at)
```

### 6. Проблемы целостности данных

#### ⚠️ Отсутствие каскадных удалений

**Проблема**: Не все связи настроены с каскадными удалениями

**Пример**:
```python
# album-svc - правильно настроено
pages: Mapped[List["Page"]] = relationship("Page", back_populates="album", cascade="all, delete-orphan")

# Но в других моделях может отсутствовать
```

#### ❌ Отсутствие проверочных ограничений

**Проблема**: Нет ограничений на значения полей

**Примеры**:
```python
# billing-svc - нет ограничений на цены
price_monthly: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

# Должно быть:
price_monthly: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, 
                                               CheckConstraint('price_monthly >= 0'))
```

### 7. Проблемы с временными метками

#### ⚠️ Использование datetime.utcnow()

**Проблема**: Устаревший способ установки временных меток

```python
# Устаревший способ
created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

# Рекомендуемый способ
created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
```

## 📊 Сводная таблица проблем

| Сервис | Миграции | Индексы | Ограничения | Каскады | Статус |
|--------|----------|---------|-------------|---------|--------|
| auth-svc | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| qr-svc | ✅ | ❌ | ❌ | ❌ | ⚠️ |
| notification-svc | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| album-svc | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| analytics-svc | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| billing-svc | ❌ | ❌ | ❌ | ❌ | ❌ |
| media-svc | ❌ | ❌ | ❌ | ❌ | ❌ |
| moderation-svc | ❌ | ❌ | ❌ | ❌ | ❌ |
| print-svc | ❌ | ❌ | ❌ | ❌ | ❌ |
| user-profile-svc | ❌ | ⚠️ | ❌ | ❌ | ❌ |

**Общий статус**: ❌ **Критические проблемы**

## 🎯 Рекомендации по исправлению

### Критический приоритет

1. **Настроить Alembic** для всех сервисов без миграций
2. **Исправить notification-svc** миграции (добавить `context.run_migrations()`)
3. **Унифицировать конфигурацию** Alembic (синхронный vs асинхронный)

### Высокий приоритет

1. **Добавить индексы** на все внешние ключи
2. **Создать составные индексы** для частых запросов
3. **Добавить ограничения** на длину полей

### Средний приоритет

1. **Настроить каскадные удаления** для всех связей
2. **Добавить проверочные ограничения** на числовые поля
3. **Обновить временные метки** на `func.now()`

## 🔧 Команды для исправления

```bash
# Инициализация Alembic для сервисов без миграций
cd apps/album-svc && alembic init alembic
cd apps/billing-svc && alembic init alembic
cd apps/media-svc && alembic init alembic
# ... и так далее для всех сервисов

# Создание миграций
cd apps/album-svc && alembic revision --autogenerate -m "Initial migration"
cd apps/billing-svc && alembic revision --autogenerate -m "Initial migration"

# Применение миграций
cd apps/album-svc && alembic upgrade head
cd apps/billing-svc && alembic upgrade head

# Проверка дрейфа схемы
cd apps/auth-svc && alembic revision --autogenerate --head head
```

## 📋 Чек-лист для каждого сервиса

- [ ] Настроен Alembic
- [ ] Созданы миграции
- [ ] Применены миграции
- [ ] Добавлены индексы на FK
- [ ] Созданы составные индексы
- [ ] Добавлены ограничения на поля
- [ ] Настроены каскадные удаления
- [ ] Добавлены проверочные ограничения
- [ ] Обновлены временные метки
- [ ] Протестированы миграции
