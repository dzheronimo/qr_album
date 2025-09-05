# 🚀 Руководство по развертыванию QR-Albums

## 📋 Содержание

1. [Предварительные требования](#предварительные-требования)
2. [Локальное развертывание](#локальное-развертывание)
3. [Развертывание в продакшене](#развертывание-в-продакшене)
4. [Настройка окружения](#настройка-окружения)
5. [Мониторинг и логирование](#мониторинг-и-логирование)
6. [Резервное копирование](#резервное-копирование)
7. [Обновление системы](#обновление-системы)
8. [Устранение неполадок](#устранение-неполадок)

## 🔧 Предварительные требования

### Системные требования

**Минимальные**:
- CPU: 2 ядра
- RAM: 4 GB
- Диск: 20 GB свободного места
- ОС: Linux (Ubuntu 20.04+), macOS, Windows 10+

**Рекомендуемые**:
- CPU: 4+ ядер
- RAM: 8+ GB
- Диск: 50+ GB SSD
- ОС: Linux (Ubuntu 22.04 LTS)

### Программное обеспечение

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+ (для разработки)
- **Git**: 2.30+
- **PostgreSQL**: 14+ (если не используете Docker)
- **Redis**: 6.0+ (если не используете Docker)
- **RabbitMQ**: 3.8+ (если не используете Docker)

### Проверка установки

```bash
# Проверка Docker
docker --version
docker-compose --version

# Проверка Python (для разработки)
python3 --version
pip3 --version

# Проверка Git
git --version
```

## 🏠 Локальное развертывание

### 1. Клонирование репозитория

```bash
git clone https://github.com/dzheronimo/qr_album.git
cd qr_album
```

### 2. Настройка окружения

```bash
# Копирование файла окружения
cp .env.example .env

# Редактирование переменных окружения
nano .env
```

**Основные переменные окружения**:

```env
# Общие настройки
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# База данных
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=qr_albums
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# JWT
JWT_SECRET_KEY=your_super_secret_jwt_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (для уведомлений)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# AI сервисы (для модерации)
OPENAI_API_KEY=your_openai_api_key
```

### 3. Запуск с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### 4. Применение миграций

```bash
# Для каждого сервиса
docker-compose exec auth-svc alembic upgrade head
docker-compose exec album-svc alembic upgrade head
docker-compose exec media-svc alembic upgrade head
docker-compose exec qr-svc alembic upgrade head
docker-compose exec user-profile-svc alembic upgrade head
docker-compose exec analytics-svc alembic upgrade head
docker-compose exec billing-svc alembic upgrade head
docker-compose exec notification-svc alembic upgrade head
docker-compose exec moderation-svc alembic upgrade head
docker-compose exec print-svc alembic upgrade head
```

### 5. Проверка работоспособности

```bash
# Проверка health checks
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
# ... и так далее для всех сервисов

# Проверка API документации
open http://localhost:8000/docs
```

## 🌐 Развертывание в продакшене

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Установка дополнительных инструментов
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 2. Настройка Nginx

```nginx
# /etc/nginx/sites-available/qr-albums
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/qr-albums /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL сертификат

```bash
# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. Настройка продакшен окружения

```bash
# Создание продакшен конфигурации
cp .env.example .env.production

# Редактирование для продакшена
nano .env.production
```

**Продакшен переменные**:

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Безопасные пароли и ключи
POSTGRES_PASSWORD=very_secure_password_here
REDIS_PASSWORD=very_secure_redis_password
JWT_SECRET_KEY=very_long_and_secure_jwt_secret_key_here

# Внешние сервисы
SMTP_HOST=your_smtp_host
SMTP_USERNAME=your_smtp_username
SMTP_PASSWORD=your_smtp_password
OPENAI_API_KEY=your_openai_api_key
```

### 5. Запуск в продакшене

```bash
# Запуск с продакшен конфигурацией
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose ps

# Мониторинг логов
docker-compose logs -f
```

## ⚙️ Настройка окружения

### Переменные окружения по сервисам

#### API Gateway
```env
API_GATEWAY_HOST=0.0.0.0
API_GATEWAY_PORT=8000
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

#### Auth Service
```env
AUTH_SVC_HOST=0.0.0.0
AUTH_SVC_PORT=8001
DATABASE_URL=postgresql://user:password@localhost:5432/auth_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Album Service
```env
ALBUM_SVC_HOST=0.0.0.0
ALBUM_SVC_PORT=8002
DATABASE_URL=postgresql://user:password@localhost:5432/album_db
REDIS_URL=redis://localhost:6379/1
```

#### Media Service
```env
MEDIA_SVC_HOST=0.0.0.0
MEDIA_SVC_PORT=8003
DATABASE_URL=postgresql://user:password@localhost:5432/media_db
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,mp4,pdf
```

#### QR Service
```env
QR_SVC_HOST=0.0.0.0
QR_SVC_PORT=8004
DATABASE_URL=postgresql://user:password@localhost:5432/qr_db
REDIS_URL=redis://localhost:6379/2
QR_BASE_URL=https://your-domain.com/qr
```

### Настройка базы данных

#### PostgreSQL

```sql
-- Создание пользователей и баз данных
CREATE USER auth_user WITH PASSWORD 'auth_password';
CREATE DATABASE auth_db OWNER auth_user;

CREATE USER album_user WITH PASSWORD 'album_password';
CREATE DATABASE album_db OWNER album_user;

CREATE USER media_user WITH PASSWORD 'media_password';
CREATE DATABASE media_db OWNER media_user;

-- И так далее для всех сервисов
```

#### Redis

```bash
# Настройка Redis
redis-cli
CONFIG SET requirepass your_redis_password
CONFIG SET maxmemory 256mb
CONFIG SET maxmemory-policy allkeys-lru
```

#### RabbitMQ

```bash
# Создание пользователей и виртуальных хостов
rabbitmqctl add_user qr_albums_user qr_albums_password
rabbitmqctl add_vhost qr_albums
rabbitmqctl set_permissions -p qr_albums qr_albums_user ".*" ".*" ".*"
```

## 📊 Мониторинг и логирование

### Health Checks

```bash
# Скрипт для проверки здоровья всех сервисов
#!/bin/bash

services=(
    "8000:API Gateway"
    "8001:Auth Service"
    "8002:Album Service"
    "8003:Media Service"
    "8004:QR Service"
    "8005:Profile Service"
    "8006:Analytics Service"
    "8007:Billing Service"
    "8008:Notification Service"
    "8009:Moderation Service"
    "8010:Print Service"
    "8011:Scan Gateway"
)

for service in "${services[@]}"; do
    port=$(echo $service | cut -d: -f1)
    name=$(echo $service | cut -d: -f2)
    
    if curl -s http://localhost:$port/health > /dev/null; then
        echo "✅ $name (port $port) - Healthy"
    else
        echo "❌ $name (port $port) - Unhealthy"
    fi
done
```

### Логирование

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f auth-svc

# Логи с фильтрацией
docker-compose logs -f | grep ERROR

# Ротация логов
docker-compose logs --tail=1000 > logs/$(date +%Y%m%d_%H%M%S).log
```

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Использование диска
df -h

# Использование памяти
free -h

# Нагрузка на CPU
top
```

## 💾 Резервное копирование

### База данных

```bash
#!/bin/bash
# backup_databases.sh

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Список баз данных
databases=(
    "auth_db"
    "album_db"
    "media_db"
    "qr_db"
    "profile_db"
    "analytics_db"
    "billing_db"
    "notification_db"
    "moderation_db"
    "print_db"
)

for db in "${databases[@]}"; do
    echo "Backing up $db..."
    docker-compose exec -T postgres pg_dump -U postgres $db > $BACKUP_DIR/${db}.sql
done

# Сжатие архива
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Медиафайлы

```bash
#!/bin/bash
# backup_media.sh

BACKUP_DIR="/backups/media/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Копирование медиафайлов
docker-compose exec -T media-svc tar -czf - /app/uploads | cat > $BACKUP_DIR/uploads.tar.gz

echo "Media backup completed: $BACKUP_DIR/uploads.tar.gz"
```

### Автоматизация резервного копирования

```bash
# Добавление в crontab
crontab -e

# Ежедневное резервное копирование в 2:00
0 2 * * * /path/to/backup_databases.sh
0 3 * * * /path/to/backup_media.sh

# Еженедельная очистка старых бэкапов
0 4 * * 0 find /backups -name "*.tar.gz" -mtime +30 -delete
```

## 🔄 Обновление системы

### Обновление кода

```bash
# Получение последних изменений
git pull origin main

# Пересборка образов
docker-compose build

# Остановка сервисов
docker-compose down

# Запуск с новыми образами
docker-compose up -d

# Применение новых миграций
docker-compose exec auth-svc alembic upgrade head
# ... и так далее для всех сервисов
```

### Обновление зависимостей

```bash
# Обновление Python зависимостей
pip install -r requirements.txt --upgrade

# Обновление Docker образов
docker-compose pull

# Пересборка с обновленными зависимостями
docker-compose build --no-cache
```

### Откат изменений

```bash
# Откат к предыдущей версии
git checkout previous-commit-hash

# Пересборка и перезапуск
docker-compose build
docker-compose down
docker-compose up -d

# Откат миграций (если необходимо)
docker-compose exec auth-svc alembic downgrade -1
```

## 🐛 Устранение неполадок

### Общие проблемы

#### Сервис не запускается

```bash
# Проверка логов
docker-compose logs service-name

# Проверка конфигурации
docker-compose config

# Проверка портов
netstat -tlnp | grep :8000
```

#### Проблемы с базой данных

```bash
# Проверка подключения к БД
docker-compose exec postgres psql -U postgres -c "SELECT 1;"

# Проверка миграций
docker-compose exec auth-svc alembic current

# Применение миграций
docker-compose exec auth-svc alembic upgrade head
```

#### Проблемы с Redis

```bash
# Проверка Redis
docker-compose exec redis redis-cli ping

# Очистка кэша
docker-compose exec redis redis-cli FLUSHALL
```

#### Проблемы с RabbitMQ

```bash
# Проверка RabbitMQ
docker-compose exec rabbitmq rabbitmqctl status

# Проверка очередей
docker-compose exec rabbitmq rabbitmqctl list_queues
```

### Мониторинг производительности

```bash
# Использование ресурсов
docker stats

# Логи с производительностью
docker-compose logs -f | grep -E "(slow|timeout|error)"

# Проверка соединений
netstat -an | grep :8000 | wc -l
```

### Восстановление после сбоев

```bash
# Перезапуск всех сервисов
docker-compose restart

# Перезапуск конкретного сервиса
docker-compose restart auth-svc

# Полная перезагрузка
docker-compose down
docker-compose up -d
```

## 📞 Поддержка

### Полезные команды

```bash
# Просмотр статуса всех сервисов
docker-compose ps

# Просмотр использования ресурсов
docker stats

# Просмотр логов в реальном времени
docker-compose logs -f

# Выполнение команд в контейнере
docker-compose exec auth-svc bash

# Проверка конфигурации
docker-compose config
```

### Контакты

- **GitHub Issues**: [Создать Issue](https://github.com/dzheronimo/qr_album/issues)
- **Email**: support@qr-albums.com
- **Документация**: [Документация проекта](https://github.com/dzheronimo/qr_album/docs)

---

*Руководство обновлено: 2024-01-01*
