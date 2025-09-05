"""
Маршруты для редиректов в Scan Gateway сервисе.

Содержит эндпоинты для обработки сканирования QR кодов
и перенаправления на соответствующие страницы.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import Settings

settings = Settings()

# Настройка rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"]
)

router = APIRouter()


@router.get("/r/{slug}")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def redirect_to_target(
    request: Request,
    slug: str
) -> RedirectResponse:
    """
    Перенаправление по короткой ссылке.
    
    Args:
        request: HTTP запрос
        slug: Slug короткой ссылки
        
    Returns:
        RedirectResponse: Редирект на целевую страницу
        
    Raises:
        HTTPException: Если ссылка не найдена
    """
    # TODO: В будущем здесь будет вызов qr-svc для получения информации о ссылке
    # и логирование аналитики через analytics-svc
    
    # Пока что возвращаем заглушку
    placeholder_url = f"https://example.com/page/{slug}"
    
    # Логирование сканирования (заглушка)
    # TODO: Отправить событие в analytics-svc
    
    return RedirectResponse(
        url=placeholder_url,
        status_code=302
    )