# py-commons

Общие утилиты и настройки для микросервисов QR-Albums.

## Установка

```bash
pip install -e .
```

## Использование

### Настройки

```python
from commons.settings import CommonSettings, DatabaseSettings

# Базовые настройки
settings = CommonSettings()

# Настройки с базой данных
db_settings = DatabaseSettings(db_name="my_service_db")
```

### JWT токены

```python
from commons.security import create_access_token, decode_token

# Создание токена
token = create_access_token(
    subject="user_123",
    secret=settings.jwt_secret,
    minutes=15
)

# Декодирование токена
payload = decode_token(token, settings.jwt_secret)
user_id = payload["sub"]
```

## Структура

- `commons/settings.py` - Базовые классы настроек
- `commons/security.py` - Утилиты для работы с JWT
