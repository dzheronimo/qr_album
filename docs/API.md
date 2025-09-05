# 📚 API Документация QR-Albums

## 📋 Содержание

1. [Обзор API](#обзор-api)
2. [Аутентификация](#аутентификация)
3. [API Gateway](#api-gateway)
4. [Auth Service](#auth-service)
5. [Album Service](#album-service)
6. [Media Service](#media-service)
7. [QR Service](#qr-service)
8. [Profile Service](#profile-service)
9. [Analytics Service](#analytics-service)
10. [Billing Service](#billing-service)
11. [Notification Service](#notification-service)
12. [Moderation Service](#moderation-service)
13. [Print Service](#print-service)
14. [Scan Gateway](#scan-gateway)
15. [Коды ошибок](#коды-ошибок)
16. [Примеры использования](#примеры-использования)

## 🌐 Обзор API

QR-Albums предоставляет RESTful API для создания и управления цифровыми альбомами с QR кодами. API построен на микросервисной архитектуре с единой точкой входа через API Gateway.

### Базовые URL

- **API Gateway**: `https://api.qr-albums.com`
- **Локальная разработка**: `http://localhost:8000`

### Формат данных

Все API используют JSON для обмена данными:

```json
{
  "data": {...},
  "message": "Success",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Версионирование

API использует версионирование через URL: `/api/v1/`

## 🔐 Аутентификация

### JWT Токены

API использует JWT (JSON Web Tokens) для аутентификации:

```http
Authorization: Bearer <access_token>
```

### Типы токенов

- **Access Token**: Короткоживущий токен для доступа к API (30 минут)
- **Refresh Token**: Долгоживущий токен для обновления access token (7 дней)

### Получение токенов

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Ответ**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Обновление токенов

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 🚪 API Gateway

### Health Check

```http
GET /health
```

**Ответ**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "auth-svc": "healthy",
    "album-svc": "healthy",
    "media-svc": "healthy"
  }
}
```

### Rate Limiting

- **Лимит**: 100 запросов в минуту на IP
- **Заголовки ответа**:
  - `X-RateLimit-Limit`: Максимальное количество запросов
  - `X-RateLimit-Remaining`: Оставшееся количество запросов
  - `X-RateLimit-Reset`: Время сброса лимита

## 👤 Auth Service

### Регистрация пользователя

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Ответ**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Вход пользователя

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### Получение профиля

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Обновление профиля

```http
PUT /api/v1/auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith"
}
```

### Сброс пароля

```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset_token_here",
  "new_password": "NewSecurePass123"
}
```

## 📚 Album Service

### Создание альбома

```http
POST /api/v1/albums
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "My Photo Album",
  "description": "Photos from my vacation",
  "is_public": true
}
```

**Ответ**:
```json
{
  "id": 1,
  "title": "My Photo Album",
  "description": "Photos from my vacation",
  "user_id": 1,
  "is_public": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Получение альбомов пользователя

```http
GET /api/v1/albums?page=1&limit=10&is_public=true
Authorization: Bearer <access_token>
```

**Ответ**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "My Photo Album",
      "description": "Photos from my vacation",
      "user_id": 1,
      "is_public": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

### Получение альбома по ID

```http
GET /api/v1/albums/{album_id}
Authorization: Bearer <access_token>
```

### Обновление альбома

```http
PUT /api/v1/albums/{album_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Album Title",
  "description": "Updated description"
}
```

### Удаление альбома

```http
DELETE /api/v1/albums/{album_id}
Authorization: Bearer <access_token>
```

### Создание страницы

```http
POST /api/v1/albums/{album_id}/pages
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Page 1",
  "content": "This is the first page of my album",
  "page_number": 1
}
```

### Получение страниц альбома

```http
GET /api/v1/albums/{album_id}/pages
Authorization: Bearer <access_token>
```

### Обновление страницы

```http
PUT /api/v1/pages/{page_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Page Title",
  "content": "Updated content"
}
```

### Удаление страницы

```http
DELETE /api/v1/pages/{page_id}
Authorization: Bearer <access_token>
```

## 🖼️ Media Service

### Загрузка файла

```http
POST /api/v1/media/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <binary_file_data>
```

**Ответ**:
```json
{
  "id": 1,
  "filename": "photo.jpg",
  "file_path": "/uploads/photo_123.jpg",
  "file_size": 1024000,
  "mime_type": "image/jpeg",
  "uploaded_at": "2024-01-01T00:00:00Z"
}
```

### Получение файла

```http
GET /api/v1/media/{media_id}
Authorization: Bearer <access_token>
```

### Привязка файла к странице

```http
POST /api/v1/media/{media_id}/attach
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "page_id": 1
}
```

### Получение файлов страницы

```http
GET /api/v1/pages/{page_id}/media
Authorization: Bearer <access_token>
```

### Удаление файла

```http
DELETE /api/v1/media/{media_id}
Authorization: Bearer <access_token>
```

### Генерация превью

```http
POST /api/v1/media/{media_id}/preview
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "width": 300,
  "height": 200,
  "quality": 80
}
```

## 📱 QR Service

### Генерация QR кода

```http
POST /api/v1/qr/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "page_id": 1,
  "album_id": 1,
  "custom_url": "https://example.com/custom-page"
}
```

**Ответ**:
```json
{
  "id": "qr_123456",
  "url": "https://qr-albums.com/qr/qr_123456",
  "qr_code_url": "https://qr-albums.com/api/v1/qr/qr_123456/image",
  "page_id": 1,
  "album_id": 1,
  "scan_count": 0,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Получение QR кода

```http
GET /api/v1/qr/{qr_id}
Authorization: Bearer <access_token>
```

### Получение изображения QR кода

```http
GET /api/v1/qr/{qr_id}/image?size=300&format=png
```

### Кастомизация QR кода

```http
PUT /api/v1/qr/{qr_id}/customize
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "foreground_color": "#000000",
  "background_color": "#FFFFFF",
  "logo_url": "https://example.com/logo.png",
  "error_correction": "M"
}
```

### Статистика сканирований

```http
GET /api/v1/qr/{qr_id}/stats
Authorization: Bearer <access_token>
```

**Ответ**:
```json
{
  "qr_id": "qr_123456",
  "scan_count": 42,
  "unique_scans": 38,
  "last_scanned_at": "2024-01-01T12:00:00Z",
  "scans_by_date": [
    {
      "date": "2024-01-01",
      "count": 5
    }
  ],
  "scans_by_location": [
    {
      "country": "US",
      "count": 20
    }
  ]
}
```

### Сканирование QR кода

```http
POST /api/v1/qr/{qr_id}/scan
Content-Type: application/json

{
  "scanner_info": {
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "location": {
      "country": "US",
      "city": "New York"
    }
  }
}
```

## 👤 Profile Service

### Получение профиля

```http
GET /api/v1/profile
Authorization: Bearer <access_token>
```

### Обновление профиля

```http
PUT /api/v1/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Photography enthusiast",
  "website": "https://johndoe.com"
}
```

### Загрузка аватарки

```http
POST /api/v1/profile/avatar
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

avatar: <binary_file_data>
```

### Настройки пользователя

```http
GET /api/v1/profile/settings
Authorization: Bearer <access_token>
```

```http
PUT /api/v1/profile/settings
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email_notifications": true,
  "push_notifications": false,
  "public_profile": true,
  "language": "en"
}
```

## 📊 Analytics Service

### Получение общей статистики

```http
GET /api/v1/analytics/overview
Authorization: Bearer <access_token>
```

**Ответ**:
```json
{
  "total_albums": 5,
  "total_pages": 25,
  "total_qr_codes": 25,
  "total_scans": 150,
  "unique_scanners": 45,
  "scans_last_30_days": 75
}
```

### Статистика альбома

```http
GET /api/v1/analytics/albums/{album_id}
Authorization: Bearer <access_token>
```

### Статистика по периодам

```http
GET /api/v1/analytics/period?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

### Экспорт данных

```http
GET /api/v1/analytics/export?format=csv&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

### Дашборды

```http
GET /api/v1/analytics/dashboards
Authorization: Bearer <access_token>
```

```http
POST /api/v1/analytics/dashboards
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Dashboard",
  "widgets": [
    {
      "type": "chart",
      "title": "Scans Over Time",
      "config": {
        "chart_type": "line",
        "data_source": "scans",
        "period": "30_days"
      }
    }
  ]
}
```

## 💳 Billing Service

### Получение тарифных планов

```http
GET /api/v1/billing/plans
Authorization: Bearer <access_token>
```

**Ответ**:
```json
{
  "plans": [
    {
      "id": 1,
      "name": "Free",
      "price": 0,
      "currency": "USD",
      "features": [
        "5 albums",
        "50 pages",
        "Basic analytics"
      ],
      "limits": {
        "albums": 5,
        "pages_per_album": 10,
        "storage_mb": 100
      }
    },
    {
      "id": 2,
      "name": "Pro",
      "price": 9.99,
      "currency": "USD",
      "features": [
        "Unlimited albums",
        "Unlimited pages",
        "Advanced analytics",
        "Custom QR codes"
      ],
      "limits": {
        "albums": -1,
        "pages_per_album": -1,
        "storage_mb": 1000
      }
    }
  ]
}
```

### Получение текущей подписки

```http
GET /api/v1/billing/subscription
Authorization: Bearer <access_token>
```

### Создание подписки

```http
POST /api/v1/billing/subscribe
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "plan_id": 2,
  "payment_method": "card",
  "billing_cycle": "monthly"
}
```

### История транзакций

```http
GET /api/v1/billing/transactions?page=1&limit=10
Authorization: Bearer <access_token>
```

### Проверка лимитов

```http
GET /api/v1/billing/limits
Authorization: Bearer <access_token>
```

**Ответ**:
```json
{
  "albums": {
    "used": 3,
    "limit": 5,
    "remaining": 2
  },
  "pages": {
    "used": 15,
    "limit": 50,
    "remaining": 35
  },
  "storage": {
    "used_mb": 45,
    "limit_mb": 100,
    "remaining_mb": 55
  }
}
```

## 🔔 Notification Service

### Получение уведомлений

```http
GET /api/v1/notifications?page=1&limit=10&unread_only=true
Authorization: Bearer <access_token>
```

### Отметка как прочитанное

```http
PUT /api/v1/notifications/{notification_id}/read
Authorization: Bearer <access_token>
```

### Настройки уведомлений

```http
GET /api/v1/notifications/settings
Authorization: Bearer <access_token>
```

```http
PUT /api/v1/notifications/settings
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email_notifications": true,
  "push_notifications": false,
  "notification_types": {
    "qr_scanned": true,
    "album_shared": true,
    "subscription_expired": true
  }
}
```

### Отправка тестового уведомления

```http
POST /api/v1/notifications/test
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "email",
  "template": "welcome"
}
```

## 🛡️ Moderation Service

### Отправка на модерацию

```http
POST /api/v1/moderation/submit
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content_type": "album",
  "content_id": 1,
  "reason": "user_report"
}
```

### Получение статуса модерации

```http
GET /api/v1/moderation/status/{moderation_id}
Authorization: Bearer <access_token>
```

### Получение правил модерации

```http
GET /api/v1/moderation/rules
Authorization: Bearer <access_token>
```

### Журнал модерации

```http
GET /api/v1/moderation/logs?page=1&limit=10
Authorization: Bearer <access_token>
```

## 🖨️ Print Service

### Создание задания печати

```http
POST /api/v1/print/jobs
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_type": "qr_label",
  "content_data": {
    "title": "My QR Label",
    "qr_code_url": "https://example.com/qr.jpg"
  },
  "print_format": "pdf",
  "template_id": 1
}
```

### Получение статуса задания

```http
GET /api/v1/print/jobs/{job_id}
Authorization: Bearer <access_token>
```

### Получение шаблонов

```http
GET /api/v1/print/templates
Authorization: Bearer <access_token>
```

### Создание шаблона

```http
POST /api/v1/print/templates
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Custom Label",
  "description": "My custom QR label template",
  "template_data": {
    "width": 100,
    "height": 50,
    "fields": [
      {
        "type": "text",
        "content": "{{title}}",
        "position": {"x": 10, "y": 10}
      },
      {
        "type": "image",
        "content": "{{qr_code_url}}",
        "position": {"x": 10, "y": 30}
      }
    ]
  }
}
```

## 📱 Scan Gateway

### Обработка сканирования

```http
GET /qr/{qr_id}
```

**Ответ**: Редирект на соответствующую страницу или JSON с данными

### Получение информации о QR коде

```http
GET /api/v1/scan/info/{qr_id}
```

**Ответ**:
```json
{
  "qr_id": "qr_123456",
  "page_id": 1,
  "album_id": 1,
  "title": "Page 1",
  "url": "https://qr-albums.com/albums/1/pages/1",
  "is_active": true
}
```

### Статистика сканирований

```http
GET /api/v1/scan/stats/{qr_id}
Authorization: Bearer <access_token>
```

## ❌ Коды ошибок

### HTTP статус коды

- **200 OK**: Успешный запрос
- **201 Created**: Ресурс создан
- **400 Bad Request**: Неверный запрос
- **401 Unauthorized**: Не авторизован
- **403 Forbidden**: Доступ запрещен
- **404 Not Found**: Ресурс не найден
- **422 Unprocessable Entity**: Ошибка валидации
- **429 Too Many Requests**: Превышен лимит запросов
- **500 Internal Server Error**: Внутренняя ошибка сервера

### Формат ошибок

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Коды ошибок

- **AUTH_INVALID_CREDENTIALS**: Неверные учетные данные
- **AUTH_TOKEN_EXPIRED**: Токен истек
- **AUTH_INSUFFICIENT_PERMISSIONS**: Недостаточно прав
- **VALIDATION_ERROR**: Ошибка валидации данных
- **RESOURCE_NOT_FOUND**: Ресурс не найден
- **RESOURCE_ALREADY_EXISTS**: Ресурс уже существует
- **RATE_LIMIT_EXCEEDED**: Превышен лимит запросов
- **BILLING_LIMIT_EXCEEDED**: Превышен лимит тарифного плана
- **FILE_TOO_LARGE**: Файл слишком большой
- **UNSUPPORTED_FILE_TYPE**: Неподдерживаемый тип файла

## 💡 Примеры использования

### Создание альбома с QR кодами

```javascript
// 1. Регистрация пользователя
const registerResponse = await fetch('/api/v1/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'johndoe',
    password: 'SecurePass123',
    first_name: 'John',
    last_name: 'Doe'
  })
});

// 2. Вход пользователя
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'SecurePass123'
  })
});

const { access_token } = await loginResponse.json();

// 3. Создание альбома
const albumResponse = await fetch('/api/v1/albums', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    title: 'My Photo Album',
    description: 'Photos from my vacation',
    is_public: true
  })
});

const album = await albumResponse.json();

// 4. Создание страницы
const pageResponse = await fetch(`/api/v1/albums/${album.id}/pages`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    title: 'Page 1',
    content: 'This is the first page',
    page_number: 1
  })
});

const page = await pageResponse.json();

// 5. Генерация QR кода
const qrResponse = await fetch('/api/v1/qr/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    page_id: page.id,
    album_id: album.id
  })
});

const qrCode = await qrResponse.json();

console.log('QR Code URL:', qrCode.qr_code_url);
```

### Загрузка и привязка медиафайла

```javascript
// 1. Загрузка файла
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/api/v1/media/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`
  },
  body: formData
});

const mediaFile = await uploadResponse.json();

// 2. Привязка к странице
const attachResponse = await fetch(`/api/v1/media/${mediaFile.id}/attach`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    page_id: page.id
  })
});
```

### Получение статистики

```javascript
// Получение общей статистики
const statsResponse = await fetch('/api/v1/analytics/overview', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const stats = await statsResponse.json();

// Получение статистики QR кода
const qrStatsResponse = await fetch(`/api/v1/qr/${qrCode.id}/stats`, {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});

const qrStats = await qrStatsResponse.json();

console.log('Total scans:', qrStats.scan_count);
console.log('Unique scanners:', qrStats.unique_scans);
```

### Python пример

```python
import requests
import json

# Базовый URL
BASE_URL = "https://api.qr-albums.com"

# 1. Регистрация пользователя
register_data = {
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
}

response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
user = response.json()

# 2. Вход пользователя
login_data = {
    "email": "user@example.com",
    "password": "SecurePass123"
}

response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
tokens = response.json()
access_token = tokens["access_token"]

# 3. Создание альбома
headers = {"Authorization": f"Bearer {access_token}"}

album_data = {
    "title": "My Photo Album",
    "description": "Photos from my vacation",
    "is_public": True
}

response = requests.post(
    f"{BASE_URL}/api/v1/albums",
    json=album_data,
    headers=headers
)
album = response.json()

# 4. Получение статистики
response = requests.get(
    f"{BASE_URL}/api/v1/analytics/overview",
    headers=headers
)
stats = response.json()

print(f"Total albums: {stats['total_albums']}")
print(f"Total scans: {stats['total_scans']}")
```

---

*API документация обновлена: 2024-01-01*
