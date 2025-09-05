# QR-Albums

Production-ready monorepo для проекта QR-Albums с использованием Python 3.12 и FastAPI микросервисов.

## Архитектура

Проект состоит из следующих микросервисов:

- **api-gateway** - API Gateway (порт 8080)
- **auth-svc** - Сервис аутентификации
- **user-profile-svc** - Сервис профилей пользователей
- **album-svc** - Сервис альбомов
- **media-svc** - Сервис медиафайлов
- **qr-svc** - Сервис QR-кодов
- **scan-gateway** - Gateway для сканирования (порт 8086)
- **print-svc** - Сервис печати
- **analytics-svc** - Сервис аналитики
- **billing-svc** - Сервис биллинга
- **notification-svc** - Сервис уведомлений
- **moderation-svc** - Сервис модерации

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Make (опционально)

### Запуск

1. Скопируйте файл с переменными окружения:
```bash
cp env.example .env
```

2. Запустите все сервисы:
```bash
make up
```

Или без Make:
```bash
docker-compose -f deploy/docker-compose.dev.yml up --build -d
```

### Проверка работоспособности

```bash
make health
```

Или вручную:
```bash
# API Gateway
curl http://localhost:8080/healthz

# Scan Gateway
curl http://localhost:8086/healthz
```

## Доступные сервисы

- **API Gateway**: http://localhost:8080
- **Scan Gateway**: http://localhost:8086
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **PostgreSQL**: localhost:5432 (postgres/postgres)

## Основные команды

```bash
# Запуск всех сервисов
make up

# Остановка всех сервисов
make down

# Просмотр логов
make logs

# Проверка здоровья сервисов
make health

# Очистка (удаление volumes)
make clean

# Форматирование кода
make fmt

# Запуск тестов
make test
```

## Структура проекта

```
qr-albums/
├── apps/                    # Микросервисы
│   ├── api-gateway/
│   ├── auth-svc/
│   ├── user-profile-svc/
│   ├── album-svc/
│   ├── media-svc/
│   ├── qr-svc/
│   ├── scan-gateway/
│   ├── print-svc/
│   ├── analytics-svc/
│   ├── billing-svc/
│   ├── notification-svc/
│   └── moderation-svc/
├── packages/               # Общие пакеты
│   └── py-commons/
├── deploy/                 # Конфигурация развертывания
│   ├── docker-compose.dev.yml
│   └── initdb/
└── .github/workflows/      # CI/CD
```

## Технологический стек

- **Backend**: Python 3.12, FastAPI, Uvicorn
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Message Queue**: RabbitMQ 3
- **Object Storage**: MinIO
- **Containerization**: Docker, Docker Compose

## Разработка

### Добавление нового сервиса

1. Создайте директорию в `apps/`
2. Добавьте базовую структуру:
   - `requirements.txt`
   - `Dockerfile`
   - `app/main.py`
   - `app/config.py`
   - `app/routes/health.py`
3. Обновите `docker-compose.dev.yml`

### Общие пакеты

Общие утилиты находятся в `packages/py-commons/`:
- JWT helpers
- Общие настройки
- Утилиты для работы с базой данных

## Лицензия

MIT