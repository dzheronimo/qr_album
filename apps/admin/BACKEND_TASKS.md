# Доработки бэкенда для админ-панели

Для полной функциональности админ-панели StoryQR необходимо реализовать следующие доработки бэкенда:

## 1. Admin Gateway (`/admin-api/v1`)

### 1.1 Создание Admin Gateway сервиса
```python
# apps/admin-gateway/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.auth import verify_admin_token, get_current_admin
from app.routes import users, events, media, orders, analytics, settings

app = FastAPI(title="StoryQR Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "https://admin.storyqr.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(media.router, prefix="/media", tags=["media"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(settings.router, prefix="/settings", tags=["settings"])
```

### 1.2 Аутентификация администраторов
```python
# apps/admin-gateway/app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import settings

security = HTTPBearer()

async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("role") not in ["superadmin", "ops", "support", "sales", "moderator", "analyst", "printer"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(token_data: dict = Depends(verify_admin_token)):
    return token_data
```

## 2. Audit Log система

### 2.1 Модель аудита
```python
# apps/admin-gateway/app/models/audit.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(String, nullable=False, index=True)
    admin_email = Column(String, nullable=False)
    action = Column(String, nullable=False)  # "user_ban", "plan_change", "refund", etc.
    entity_type = Column(String, nullable=False)  # "user", "event", "order", etc.
    entity_id = Column(String, nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2.2 Сервис аудита
```python
# apps/admin-gateway/app/services/audit.py
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.database import get_db
from typing import Optional, Dict, Any

class AuditService:
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        admin_id: str,
        admin_email: str,
        action: str,
        entity_type: str,
        entity_id: str,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        audit_log = AuditLog(
            admin_id=admin_id,
            admin_email=admin_email,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(audit_log)
        self.db.commit()
```

## 3. Расширение существующих сервисов

### 3.1 User Service - добавление админ методов
```python
# apps/user-profile-svc/app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.user_service import UserService
from app.auth import get_current_admin
from app.services.audit import AuditService

router = APIRouter()

@router.get("/users")
async def get_users(
    query: Optional[str] = None,
    role: Optional[str] = None,
    plan: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    admin = Depends(get_current_admin),
    user_service: UserService = Depends(),
    audit_service: AuditService = Depends()
):
    users = await user_service.get_users_paginated(
        query=query, role=role, plan=plan, page=page, limit=limit
    )
    
    audit_service.log_action(
        admin_id=admin["sub"],
        admin_email=admin["email"],
        action="users_list_view",
        entity_type="users",
        entity_id="list"
    )
    
    return users

@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: str,
    admin = Depends(get_current_admin),
    user_service: UserService = Depends(),
    audit_service: AuditService = Depends()
):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_status = user.status
    await user_service.ban_user(user_id)
    
    audit_service.log_action(
        admin_id=admin["sub"],
        admin_email=admin["email"],
        action="user_ban",
        entity_type="user",
        entity_id=user_id,
        old_values={"status": old_status},
        new_values={"status": "banned"}
    )
    
    return {"message": "User banned successfully"}
```

### 3.2 Billing Service - добавление админ методов
```python
# apps/billing-svc/app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.billing_service import BillingService
from app.auth import get_current_admin

router = APIRouter()

@router.post("/orders/{order_id}/mark-paid")
async def mark_order_paid(
    order_id: str,
    admin = Depends(get_current_admin),
    billing_service: BillingService = Depends()
):
    order = await billing_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    await billing_service.mark_order_paid(order_id, admin["sub"])
    return {"message": "Order marked as paid"}

@router.post("/orders/{order_id}/refund")
async def refund_order(
    order_id: str,
    amount: Optional[float] = None,
    admin = Depends(get_current_admin),
    billing_service: BillingService = Depends()
):
    order = await billing_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    refund_amount = amount or order.amount
    await billing_service.process_refund(order_id, refund_amount, admin["sub"])
    return {"message": f"Refund processed for {refund_amount}"}
```

### 3.3 Analytics Service - создание нового сервиса
```python
# apps/analytics-svc/app/main.py
from fastapi import FastAPI
from app.routes import overview, revenue, funnels, cohorts

app = FastAPI(title="StoryQR Analytics Service")

app.include_router(overview.router, prefix="/overview", tags=["overview"])
app.include_router(revenue.router, prefix="/revenue", tags=["revenue"])
app.include_router(funnels.router, prefix="/funnels", tags=["funnels"])
app.include_router(cohorts.router, prefix="/cohorts", tags=["cohorts"])
```

```python
# apps/analytics-svc/app/services/analytics_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, List, Any

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_overview_metrics(self, from_date: str, to_date: str) -> Dict[str, Any]:
        query = text("""
            SELECT 
                COUNT(DISTINCT u.id) as total_users,
                COUNT(DISTINCT CASE WHEN u.last_login_at >= :from_date THEN u.id END) as active_users,
                COUNT(DISTINCT e.id) as total_events,
                COUNT(DISTINCT CASE WHEN e.status = 'active' THEN e.id END) as active_events,
                COALESCE(SUM(o.amount), 0) as total_revenue,
                COUNT(DISTINCT o.id) as total_orders
            FROM users u
            LEFT JOIN events e ON u.id = e.owner_id
            LEFT JOIN orders o ON u.id = o.user_id 
                AND o.status = 'paid' 
                AND o.created_at BETWEEN :from_date AND :to_date
        """)
        
        result = self.db.execute(query, {
            "from_date": from_date,
            "to_date": to_date
        }).fetchone()
        
        return {
            "total_users": result.total_users,
            "active_users": result.active_users,
            "total_events": result.total_events,
            "active_events": result.active_events,
            "total_revenue": float(result.total_revenue),
            "total_orders": result.total_orders
        }
    
    async def get_revenue_data(
        self, 
        granularity: str, 
        from_date: str, 
        to_date: str,
        currency: str = "RUB"
    ) -> Dict[str, Any]:
        if granularity == "day":
            date_format = "%Y-%m-%d"
        elif granularity == "week":
            date_format = "%Y-%u"
        elif granularity == "month":
            date_format = "%Y-%m"
        else:
            raise ValueError("Invalid granularity")
        
        query = text(f"""
            SELECT 
                DATE_FORMAT(created_at, '{date_format}') as period,
                SUM(amount) as revenue,
                COUNT(*) as orders
            FROM orders 
            WHERE status = 'paid' 
                AND created_at BETWEEN :from_date AND :to_date
                AND currency = :currency
            GROUP BY period
            ORDER BY period
        """)
        
        results = self.db.execute(query, {
            "from_date": from_date,
            "to_date": to_date,
            "currency": currency
        }).fetchall()
        
        return {
            "data": [
                {
                    "period": row.period,
                    "revenue": float(row.revenue),
                    "orders": row.orders
                }
                for row in results
            ],
            "currency": currency
        }
```

## 4. Print Service - расширение функциональности

### 4.1 Добавление админ методов
```python
# apps/print-svc/app/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.print_service import PrintService
from app.auth import get_current_admin

router = APIRouter()

@router.get("/print/orders")
async def get_print_orders(
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    admin = Depends(get_current_admin),
    print_service: PrintService = Depends()
):
    return await print_service.get_orders_paginated(
        status=status, page=page, limit=limit
    )

@router.post("/print/orders/{order_id}/status")
async def update_print_order_status(
    order_id: str,
    status: str,
    tracking: Optional[str] = None,
    admin = Depends(get_current_admin),
    print_service: PrintService = Depends()
):
    await print_service.update_order_status(order_id, status, tracking, admin["sub"])
    return {"message": "Order status updated"}

@router.get("/print/orders/{order_id}/export")
async def export_print_order(
    order_id: str,
    admin = Depends(get_current_admin),
    print_service: PrintService = Depends()
):
    return await print_service.export_order_data(order_id)
```

## 5. System Monitoring

### 5.1 Logs Service
```python
# apps/system-svc/app/routes/logs.py
from fastapi import APIRouter, Depends, Query
from app.services.log_service import LogService
from app.auth import get_current_admin

router = APIRouter()

@router.get("/system/logs")
async def get_system_logs(
    service: Optional[str] = None,
    level: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 100,
    admin = Depends(get_current_admin),
    log_service: LogService = Depends()
):
    return await log_service.get_logs(
        service=service, level=level, query=query, limit=limit
    )
```

### 5.2 Webhooks Service
```python
# apps/system-svc/app/routes/webhooks.py
from fastapi import APIRouter, Depends
from app.services.webhook_service import WebhookService
from app.auth import get_current_admin

router = APIRouter()

@router.get("/system/webhooks")
async def get_webhook_logs(
    provider: Optional[str] = None,
    limit: int = 50,
    admin = Depends(get_current_admin),
    webhook_service: WebhookService = Depends()
):
    return await webhook_service.get_webhook_logs(
        provider=provider, limit=limit
    )

@router.post("/system/webhooks/{webhook_id}/replay")
async def replay_webhook(
    webhook_id: str,
    admin = Depends(get_current_admin),
    webhook_service: WebhookService = Depends()
):
    return await webhook_service.replay_webhook(webhook_id)
```

## 6. Database Migrations

### 6.1 Создание таблиц для админки
```sql
-- apps/admin-gateway/migrations/001_create_admin_tables.sql

-- Audit logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(255) NOT NULL,
    admin_email VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_admin_id ON audit_logs(admin_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Admin users table
CREATE TABLE admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    permissions TEXT[],
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_role ON admin_users(role);
```

## 7. Docker Compose обновления

### 7.1 Добавление новых сервисов
```yaml
# docker-compose.yml
services:
  admin-gateway:
    build: ./apps/admin-gateway
    ports:
      - "8081:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://storyqr:storyqr@postgres:5432/storyqr_admin
      - JWT_SECRET=${JWT_SECRET}
      - USER_SERVICE_URL=http://user-profile-svc:8000
      - BILLING_SERVICE_URL=http://billing-svc:8000
      - ANALYTICS_SERVICE_URL=http://analytics-svc:8000
    depends_on:
      - postgres
      - user-profile-svc
      - billing-svc
      - analytics-svc

  analytics-svc:
    build: ./apps/analytics-svc
    ports:
      - "8009:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://storyqr:storyqr@postgres:5432/storyqr_analytics
    depends_on:
      - postgres

  system-svc:
    build: ./apps/system-svc
    ports:
      - "8010:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://storyqr:storyqr@postgres:5432/storyqr_system
      - LOKI_URL=http://loki:3100
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672
    depends_on:
      - postgres
      - loki
      - rabbitmq
```

## 8. Приоритеты реализации

### Высокий приоритет (MVP)
1. ✅ Admin Gateway с базовой аутентификацией
2. ✅ Audit Log система
3. ✅ Расширение User Service админ методами
4. ✅ Расширение Billing Service админ методами
5. ✅ Базовые настройки (тарифы, триал)

### Средний приоритет
1. Analytics Service с базовыми метриками
2. Расширение Print Service
3. System Monitoring (логи, webhooks)
4. Полная RBAC система

### Низкий приоритет
1. Продвинутая аналитика (когорты, воронки)
2. Система уведомлений
3. Интеграция с внешними мониторинговыми системами
4. Автоматизация и скрипты

## 9. Тестирование

### 9.1 Unit тесты для админ методов
```python
# apps/admin-gateway/tests/test_admin_routes.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_users_requires_auth():
    response = client.get("/users")
    assert response.status_code == 401

def test_ban_user_success():
    # Mock authentication
    headers = {"Authorization": "Bearer valid_admin_token"}
    response = client.post("/users/123/ban", headers=headers)
    assert response.status_code == 200
    assert "banned successfully" in response.json()["message"]
```

### 9.2 Integration тесты
```python
# apps/admin-gateway/tests/test_integration.py
import pytest
from app.services.audit import AuditService
from app.database import get_db

def test_audit_log_creation():
    db = next(get_db())
    audit_service = AuditService(db)
    
    audit_service.log_action(
        admin_id="admin123",
        admin_email="admin@example.com",
        action="user_ban",
        entity_type="user",
        entity_id="user456"
    )
    
    # Verify audit log was created
    audit_logs = db.query(AuditLog).filter_by(admin_id="admin123").all()
    assert len(audit_logs) == 1
    assert audit_logs[0].action == "user_ban"
```

## 10. Документация API

### 10.1 OpenAPI спецификация
```python
# apps/admin-gateway/app/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="StoryQR Admin API",
    description="Административный API для управления StoryQR",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="StoryQR Admin API",
        version="1.0.0",
        description="Административный API для управления StoryQR",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

Этот план обеспечивает полную функциональность админ-панели с минимальными изменениями в существующей архитектуре.


