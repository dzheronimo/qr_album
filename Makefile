# Makefile для проекта QR-Albums

.PHONY: help install test test-unit test-integration test-e2e test-coverage clean lint format

# Цвета для вывода
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

help: ## Показать справку
	@echo "$(BLUE)QR-Albums Project$(NC)"
	@echo "$(BLUE)===============$(NC)"
	@echo ""
	@echo "$(GREEN)Доступные команды:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Установить зависимости
	@echo "$(BLUE)Установка зависимостей...$(NC)"
	pip install -r requirements.txt
	pip install -r tests/requirements.txt
	@echo "$(GREEN)Зависимости установлены!$(NC)"

install-dev: ## Установить зависимости для разработки
	@echo "$(BLUE)Установка зависимостей для разработки...$(NC)"
	pip install -r requirements.txt
	pip install -r tests/requirements.txt
	pip install -r requirements-dev.txt
	@echo "$(GREEN)Зависимости для разработки установлены!$(NC)"

test: ## Запустить все тесты
	@echo "$(BLUE)Запуск всех тестов...$(NC)"
	pytest tests/ -v
	@echo "$(GREEN)Все тесты завершены!$(NC)"

test-unit: ## Запустить только unit тесты
	@echo "$(BLUE)Запуск unit тестов...$(NC)"
	pytest tests/unit/ -v -m "unit"
	@echo "$(GREEN)Unit тесты завершены!$(NC)"

test-integration: ## Запустить только integration тесты
	@echo "$(BLUE)Запуск integration тестов...$(NC)"
	pytest tests/integration/ -v -m "integration"
	@echo "$(GREEN)Integration тесты завершены!$(NC)"

test-e2e: ## Запустить только E2E тесты
	@echo "$(BLUE)Запуск E2E тестов...$(NC)"
	pytest tests/e2e/ -v -m "e2e"
	@echo "$(GREEN)E2E тесты завершены!$(NC)"

test-fast: ## Запустить быстрые тесты (без slow)
	@echo "$(BLUE)Запуск быстрых тестов...$(NC)"
	pytest tests/ -v -m "not slow"
	@echo "$(GREEN)Быстрые тесты завершены!$(NC)"

test-coverage: ## Запустить тесты с покрытием кода
	@echo "$(BLUE)Запуск тестов с покрытием кода...$(NC)"
	pytest tests/ --cov=apps --cov=packages --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Тесты с покрытием завершены! Отчет в htmlcov/index.html$(NC)"

test-parallel: ## Запустить тесты параллельно
	@echo "$(BLUE)Запуск тестов параллельно...$(NC)"
	pytest tests/ -n auto
	@echo "$(GREEN)Параллельные тесты завершены!$(NC)"

test-auth: ## Запустить тесты аутентификации
	@echo "$(BLUE)Запуск тестов аутентификации...$(NC)"
	pytest tests/ -v -m "auth"
	@echo "$(GREEN)Тесты аутентификации завершены!$(NC)"

test-album: ## Запустить тесты альбомов
	@echo "$(BLUE)Запуск тестов альбомов...$(NC)"
	pytest tests/ -v -m "album"
	@echo "$(GREEN)Тесты альбомов завершены!$(NC)"

test-media: ## Запустить тесты медиафайлов
	@echo "$(BLUE)Запуск тестов медиафайлов...$(NC)"
	pytest tests/ -v -m "media"
	@echo "$(GREEN)Тесты медиафайлов завершены!$(NC)"

test-qr: ## Запустить тесты QR кодов
	@echo "$(BLUE)Запуск тестов QR кодов...$(NC)"
	pytest tests/ -v -m "qr"
	@echo "$(GREEN)Тесты QR кодов завершены!$(NC)"

test-billing: ## Запустить тесты биллинга
	@echo "$(BLUE)Запуск тестов биллинга...$(NC)"
	pytest tests/ -v -m "billing"
	@echo "$(GREEN)Тесты биллинга завершены!$(NC)"

test-notification: ## Запустить тесты уведомлений
	@echo "$(BLUE)Запуск тестов уведомлений...$(NC)"
	pytest tests/ -v -m "notification"
	@echo "$(GREEN)Тесты уведомлений завершены!$(NC)"

test-moderation: ## Запустить тесты модерации
	@echo "$(BLUE)Запуск тестов модерации...$(NC)"
	pytest tests/ -v -m "moderation"
	@echo "$(GREEN)Тесты модерации завершены!$(NC)"

test-print: ## Запустить тесты печати
	@echo "$(BLUE)Запуск тестов печати...$(NC)"
	pytest tests/ -v -m "print"
	@echo "$(GREEN)Тесты печати завершены!$(NC)"

lint: ## Запустить линтеры
	@echo "$(BLUE)Запуск линтеров...$(NC)"
	flake8 apps/ packages/ tests/
	black --check apps/ packages/ tests/
	isort --check-only apps/ packages/ tests/
	@echo "$(GREEN)Линтеры завершены!$(NC)"

format: ## Форматировать код
	@echo "$(BLUE)Форматирование кода...$(NC)"
	black apps/ packages/ tests/
	isort apps/ packages/ tests/
	@echo "$(GREEN)Код отформатирован!$(NC)"

clean: ## Очистить временные файлы
	@echo "$(BLUE)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	@echo "$(GREEN)Очистка завершена!$(NC)"

setup-db: ## Настроить тестовые базы данных
	@echo "$(BLUE)Настройка тестовых баз данных...$(NC)"
	# Создание тестовых баз данных
	# Здесь можно добавить команды для создания тестовых БД
	@echo "$(GREEN)Тестовые базы данных настроены!$(NC)"

docker-test: ## Запустить тесты в Docker
	@echo "$(BLUE)Запуск тестов в Docker...$(NC)"
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@echo "$(GREEN)Тесты в Docker завершены!$(NC)"

ci: ## Запустить CI pipeline
	@echo "$(BLUE)Запуск CI pipeline...$(NC)"
	make lint
	make test-coverage
	@echo "$(GREEN)CI pipeline завершен!$(NC)"

# Команды для разработки
dev-setup: install-dev setup-db ## Настроить среду разработки
	@echo "$(GREEN)Среда разработки настроена!$(NC)"

dev-test: test-fast ## Быстрые тесты для разработки
	@echo "$(GREEN)Быстрые тесты для разработки завершены!$(NC)"

# Команды для продакшена
prod-test: test ## Тесты для продакшена
	@echo "$(GREEN)Тесты для продакшена завершены!$(NC)"

# Статистика
stats: ## Показать статистику проекта
	@echo "$(BLUE)Статистика проекта:$(NC)"
	@echo "Файлы Python: $$(find . -name '*.py' | wc -l)"
	@echo "Строки кода: $$(find . -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@echo "Тесты: $$(find tests/ -name 'test_*.py' | wc -l)"
	@echo "Строки тестов: $$(find tests/ -name 'test_*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}')"