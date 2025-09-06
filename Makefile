# StoryQR Docker Management

.PHONY: help build up down logs clean restart status

# Default target
help:
	@echo "StoryQR Docker Management Commands:"
	@echo ""
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - Show logs for all services"
	@echo "  make status    - Show status of all services"
	@echo "  make clean     - Remove all containers and volumes"
	@echo ""
	@echo "Frontend specific:"
	@echo "  make web-build - Build only frontend"
	@echo "  make web-logs  - Show frontend logs"
	@echo ""
	@echo "Backend specific:"
	@echo "  make backend-build - Build only backend services"
	@echo "  make backend-logs  - Show backend logs"
	@echo ""

# Build all services
build:
	@echo "Building all Docker images..."
	docker-compose build

# Build only frontend
web-build:
	@echo "Building frontend..."
	docker-compose build web

# Build only backend services
backend-build:
	@echo "Building backend services..."
	docker-compose build api-gateway auth-svc album-svc media-svc qr-svc user-profile-svc analytics-svc billing-svc notification-svc moderation-svc print-svc scan-gateway

# Start all services
up:
	@echo "Starting all services..."
	docker-compose up -d

# Stop all services
down:
	@echo "Stopping all services..."
	docker-compose down

# Restart all services
restart: down up

# Show logs for all services
logs:
	docker-compose logs -f

# Show frontend logs
web-logs:
	docker-compose logs -f web

# Show backend logs
backend-logs:
	docker-compose logs -f api-gateway auth-svc album-svc media-svc qr-svc user-profile-svc analytics-svc billing-svc notification-svc moderation-svc print-svc scan-gateway

# Show status of all services
status:
	@echo "Service Status:"
	@docker-compose ps

# Clean up everything
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development commands
dev:
	@echo "Starting development environment..."
	docker-compose -f docker-compose.dev.yml up -d

dev-down:
	@echo "Stopping development environment..."
	docker-compose -f docker-compose.dev.yml down

# Production commands
prod:
	@echo "Starting production environment..."
	docker-compose up -d

prod-down:
	@echo "Stopping production environment..."
	docker-compose down

# Database commands
db-migrate:
	@echo "Running database migrations..."
	docker-compose exec api-gateway python -m alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres
	sleep 10
	docker-compose up -d

# Health check
health:
	@echo "Checking service health..."
	@echo "Frontend: http://localhost:3000"
	@echo "API Gateway: http://localhost:8080"
	@echo "Database: localhost:5432"
	@echo "Redis: localhost:6379"
	@echo "RabbitMQ: http://localhost:15672"
	@echo "MinIO: http://localhost:9001"
	@echo "MailHog: http://localhost:8025"