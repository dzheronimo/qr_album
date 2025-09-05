.PHONY: up down fmt test clean logs

# Start all services
up:
	docker-compose -f deploy/docker-compose.dev.yml up --build -d

# Stop all services
down:
	docker-compose -f deploy/docker-compose.dev.yml down

# Stop and remove volumes
clean:
	docker-compose -f deploy/docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f

# Format code
fmt:
	docker-compose -f deploy/docker-compose.dev.yml exec api-gateway python -m black .
	docker-compose -f deploy/docker-compose.dev.yml exec api-gateway python -m isort .

# Run tests
test:
	docker-compose -f deploy/docker-compose.dev.yml exec qr-svc python -m pytest

# Show logs
logs:
	docker-compose -f deploy/docker-compose.dev.yml logs -f

# Health check
health:
	@echo "Checking API Gateway health..."
	@curl -f http://localhost:8080/healthz || echo "API Gateway is not healthy"
	@echo "Checking Scan Gateway health..."
	@curl -f http://localhost:8086/healthz || echo "Scan Gateway is not healthy"

# Install dependencies locally (for development)
install:
	pip install -r packages/py-commons/requirements.txt

# Database migrations
migrate:
	docker-compose -f deploy/docker-compose.dev.yml exec qr-svc alembic upgrade head

# Create new migration
migration:
	docker-compose -f deploy/docker-compose.dev.yml exec qr-svc alembic revision --autogenerate -m "$(msg)"