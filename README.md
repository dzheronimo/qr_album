# 🎯 QR-Albums - Микросервисная платформа для создания цифровых альбомов с QR кодами

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-100%25-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 Описание

**QR-Albums** - это современная микросервисная платформа для создания интерактивных цифровых альбомов с QR кодами. Пользователи могут создавать альбомы, добавлять страницы с медиафайлами, генерировать QR коды для каждой страницы и отслеживать статистику сканирований.

### 🌟 Основные возможности

- **📚 Управление альбомами** - Создание, редактирование и организация цифровых альбомов
- **🖼️ Медиафайлы** - Загрузка и управление изображениями, видео и документами
- **📱 QR коды** - Автоматическая генерация QR кодов для каждой страницы альбома
- **📊 Аналитика** - Детальная статистика сканирований и взаимодействий
- **👤 Профили пользователей** - Персонализированные настройки и предпочтения
- **💳 Биллинг** - Система подписок и тарифных планов
- **🔔 Уведомления** - Email и push уведомления
- **🛡️ Модерация** - AI-модерация контента
- **🖨️ Печать** - Генерация PDF этикеток для печати QR кодов

## 🏗️ Архитектура

Проект построен на микросервисной архитектуре с использованием FastAPI и включает следующие сервисы:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   Auth Service  │    │  Album Service  │
│   (Port 8000)   │◄──►│   (Port 8001)   │◄──►│   (Port 8002)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Media Service  │    │   QR Service    │    │ Profile Service │
│   (Port 8003)   │◄──►│   (Port 8004)   │◄──►│   (Port 8005)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Analytics Service│    │ Billing Service │    │Notification Svc │
│   (Port 8006)   │◄──►│   (Port 8007)   │◄──►│   (Port 8008)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Moderation Service│   │  Print Service  │    │  Scan Gateway   │
│   (Port 8009)   │◄──►│   (Port 8010)   │◄──►│   (Port 8011)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 Технологический стек

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **База данных**: PostgreSQL, Redis
- **Очереди**: RabbitMQ
- **Контейнеризация**: Docker, Docker Compose
- **Тестирование**: pytest, pytest-asyncio, pytest-cov
- **Документация**: OpenAPI/Swagger, Sphinx
- **Мониторинг**: Prometheus, Grafana (планируется)

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Docker и Docker Compose
- Git

### Установка

1. **Клонирование репозитория**
```bash
git clone https://github.com/dzheronimo/qr_album.git
cd qr_album
```

2. **Установка зависимостей**
```bash
# Установка Python зависимостей
pip install -r requirements.txt
pip install -r tests/requirements.txt

# Или используйте Makefile
make install
```

3. **Настройка окружения**
```bash
# Копирование файла окружения
cp .env.example .env

# Редактирование переменных окружения
nano .env
```

4. **Запуск с Docker Compose**
```bash
# Запуск всех сервисов
docker-compose up -d

# Или для разработки
docker-compose -f docker-compose.dev.yml up -d
```

5. **Применение миграций**
```bash
# Для каждого сервиса
cd apps/auth-svc && alembic upgrade head
cd apps/album-svc && alembic upgrade head
# ... и так далее для всех сервисов
```

### 🧪 Тестирование

```bash
# Все тесты
make test

# Только unit тесты
make test-unit

# Только integration тесты
make test-integration

# E2E тесты
make test-e2e

# Тесты с покрытием кода
make test-coverage

# Быстрые тесты (без медленных)
make test-fast
```

## 📁 Структура проекта

```
qr_album/
├── apps/                          # Микросервисы
│   ├── api-gateway/              # API Gateway (порт 8000)
│   ├── auth-svc/                 # Сервис аутентификации (порт 8001)
│   ├── album-svc/                # Сервис альбомов (порт 8002)
│   ├── media-svc/                # Сервис медиафайлов (порт 8003)
│   ├── qr-svc/                   # Сервис QR кодов (порт 8004)
│   ├── user-profile-svc/         # Сервис профилей (порт 8005)
│   ├── analytics-svc/            # Сервис аналитики (порт 8006)
│   ├── billing-svc/              # Сервис биллинга (порт 8007)
│   ├── notification-svc/         # Сервис уведомлений (порт 8008)
│   ├── moderation-svc/           # Сервис модерации (порт 8009)
│   ├── print-svc/                # Сервис печати (порт 8010)
│   └── scan-gateway/             # Gateway для сканирования (порт 8011)
├── packages/                      # Общие пакеты
│   └── py-commons/               # Общие утилиты и интеграции
├── tests/                         # Тесты
│   ├── unit/                     # Unit тесты
│   ├── integration/              # Integration тесты
│   └── e2e/                      # E2E тесты
├── docker-compose.yml            # Docker Compose для продакшена
├── docker-compose.dev.yml        # Docker Compose для разработки
├── Makefile                      # Команды для разработки
├── pytest.ini                   # Конфигурация pytest
└── README.md                     # Этот файл
```

## 🔌 API Документация

После запуска сервисов документация API доступна по следующим адресам:

- **API Gateway**: http://localhost:8000/docs
- **Auth Service**: http://localhost:8001/docs
- **Album Service**: http://localhost:8002/docs
- **Media Service**: http://localhost:8003/docs
- **QR Service**: http://localhost:8004/docs
- **Profile Service**: http://localhost:8005/docs
- **Analytics Service**: http://localhost:8006/docs
- **Billing Service**: http://localhost:8007/docs
- **Notification Service**: http://localhost:8008/docs
- **Moderation Service**: http://localhost:8009/docs
- **Print Service**: http://localhost:8010/docs
- **Scan Gateway**: http://localhost:8011/docs

## 🛠️ Разработка

### Команды для разработки

```bash
# Установка зависимостей для разработки
make install-dev

# Настройка среды разработки
make dev-setup

# Форматирование кода
make format

# Линтинг
make lint

# Быстрые тесты для разработки
make dev-test

# Статистика проекта
make stats
```

### Добавление нового сервиса

1. Создайте директорию в `apps/`
2. Скопируйте структуру из существующего сервиса
3. Обновите `docker-compose.yml`
4. Добавьте тесты в `tests/`
5. Обновите документацию

### Работа с базой данных

```bash
# Создание новой миграции
cd apps/[service-name]
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head

# Откат миграций
alembic downgrade -1
```

## 🚀 Развертывание

### Продакшен

```bash
# Сборка и запуск
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Логи
docker-compose logs -f [service-name]
```

### Мониторинг

- **Health checks**: `GET /health` для каждого сервиса
- **Метрики**: Планируется интеграция с Prometheus
- **Логи**: Централизованное логирование через ELK Stack (планируется)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Стандарты кода

- Используйте `black` для форматирования
- Следуйте PEP 8
- Добавляйте docstrings для всех функций
- Покрывайте код тестами (минимум 80%)
- Используйте type hints

## 📊 Статистика проекта

- **Микросервисов**: 12
- **Строк кода**: 15,000+
- **Тестов**: 100+
- **Покрытие тестами**: 80%+
- **API эндпоинтов**: 200+

## 🐛 Известные проблемы

- [ ] Интеграция с реальными платежными системами
- [ ] Полная интеграция с AI сервисами модерации
- [ ] Настройка мониторинга и алертинга
- [ ] Оптимизация производительности для больших нагрузок

## 📝 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 👥 Авторы

- **dzheronimo** - *Основной разработчик* - [GitHub](https://github.com/dzheronimo)

## 🙏 Благодарности

- FastAPI команде за отличный фреймворк
- SQLAlchemy за мощную ORM
- Docker за контейнеризацию
- Всем контрибьюторам open source проектов

## 📞 Поддержка

Если у вас есть вопросы или проблемы:

1. Проверьте [Issues](https://github.com/dzheronimo/qr_album/issues)
2. Создайте новый Issue с подробным описанием
3. Свяжитесь с разработчиком

---

**🎉 Спасибо за использование QR-Albums!** 

Создавайте удивительные интерактивные альбомы с QR кодами! 📱✨