# Порты сервисов QR-Albums

Этот документ содержит актуальную информацию о портах всех сервисов в системе QR-Albums.

## Frontend сервисы

| Сервис | Внешний порт | Внутренний порт | Описание |
|--------|--------------|-----------------|----------|
| Web (Next.js) | 3000 | 3000 | Основное веб-приложение |
| Admin Panel | 3001 | 3001 | Панель администратора |

## API Gateway

| Сервис | Внешний порт | Внутренний порт | Описание |
|--------|--------------|-----------------|----------|
| API Gateway | 8080 | 8000 | Основной API Gateway |

## Микросервисы

| Сервис | Внешний порт | Внутренний порт | Описание |
|--------|--------------|-----------------|----------|
| Auth Service | 8001 | 8000 | Аутентификация и авторизация |
| Album Service | 8002 | 8000 | Управление альбомами |
| Media Service | 8003 | 8000 | Управление медиафайлами |
| QR Service | 8005 | 8000 | Генерация QR-кодов |
| User Profile Service | 8006 | 8000 | Профили пользователей |
| Analytics Service | 8007 | 8000 | Аналитика и метрики |
| Billing Service | 8008 | 8000 | Биллинг и платежи |
| Notification Service | 8009 | 8000 | Уведомления |
| Moderation Service | 8010 | 8000 | Модерация контента |
| Print Service | 8011 | 8000 | Генерация PDF |

## Gateway сервисы

| Сервис | Внешний порт | Внутренний порт | Описание |
|--------|--------------|-----------------|----------|
| Scan Gateway | 8086 | 8000 | Обработка сканирования QR-кодов |

## Инфраструктурные сервисы

| Сервис | Внешний порт | Внутренний порт | Описание |
|--------|--------------|-----------------|----------|
| PostgreSQL | 5432 | 5432 | Основная база данных |
| Redis | 6379 | 6379 | Кэш и сессии |
| RabbitMQ | 5672 | 5672 | Очереди сообщений |
| RabbitMQ Management | 15672 | 15672 | Веб-интерфейс RabbitMQ |
| MinIO | 9000 | 9000 | Объектное хранилище |
| MinIO Console | 9001 | 9001 | Веб-интерфейс MinIO |
| MailHog SMTP | 1025 | 1025 | Тестовый SMTP сервер |
| MailHog Web | 8025 | 8025 | Веб-интерфейс MailHog |

## Health Endpoints

Все микросервисы предоставляют следующие health endpoints:

- `GET /health` - Liveness probe (проверка, что сервис работает)
- `GET /health/ready` - Readiness probe (проверка готовности принимать запросы)
- `GET /healthz` - Legacy health endpoint (для совместимости)

## Примеры использования

### Проверка здоровья сервиса
```bash
curl http://localhost:8001/health
curl http://localhost:8001/health/ready
```

### Доступ к веб-интерфейсам
- Web приложение: http://localhost:3000
- Admin панель: http://localhost:3001
- RabbitMQ Management: http://localhost:15672
- MinIO Console: http://localhost:9001
- MailHog: http://localhost:8025

### API Gateway
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/albums
```

### Scan Gateway
```bash
curl http://localhost:8086/health
curl http://localhost:8086/qr/example-slug
```

## Сетевая конфигурация

Все сервисы работают в Docker сети `storyqr-network` и могут обращаться друг к другу по именам сервисов:

- `http://api-gateway:8000`
- `http://auth-svc:8000`
- `http://postgres:5432`
- `http://redis:6379`
- `http://rabbit:5672`
- `http://minio:9000`

## Безопасность

- Все внешние порты должны быть защищены файрволом в production
- Внутренние порты доступны только внутри Docker сети
- Health endpoints не требуют аутентификации
- API endpoints защищены JWT токенами

## Мониторинг

Для мониторинга состояния сервисов используйте:

```bash
# Проверка статуса всех контейнеров
docker-compose ps

# Проверка логов
docker-compose logs -f [service-name]

# Проверка health checks
docker inspect [container-name] | grep -A 10 Health
```

---

**Примечание**: Этот документ автоматически генерируется на основе конфигурации docker-compose.yml. При изменении портов обновите соответствующие файлы конфигурации.
