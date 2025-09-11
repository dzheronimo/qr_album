from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware

from app.routes import health, proxy, auth
from app.middleware import AuthMiddleware, RateLimitMiddleware, LoggingMiddleware
from app.config import Settings

settings = Settings()

app = FastAPI(
    title="API Gateway",
    description="API Gateway для QR-Albums",
    version="1.0.0",
)

# Добавляем middleware в правильном порядке
# В FastAPI middleware добавляется в обратном порядке
# Аутентификация должна быть последней (первой в списке)
app.add_middleware(AuthMiddleware)

# Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, requests_per_hour=1000)

# Логирование
app.add_middleware(LoggingMiddleware)

# CORS должен быть первым (последним в списке)
app.add_middleware(
    FastAPICORSMiddleware,
    allow_origins=settings.cors_origins,  # Безопасные домены из конфигурации
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Подключение маршрутов
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, tags=["auth"])
app.include_router(auth.router, prefix="/api/v1", tags=["api-auth"])
app.include_router(auth.router, prefix="/admin-api/v1", tags=["admin-auth"])
app.include_router(proxy.router, prefix="/api/v1", tags=["api-proxy"])
