"""
Маршруты для работы с QR кодами и короткими ссылками.

Содержит эндпоинты для создания коротких ссылок и генерации QR кодов.
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import segno
from hashids import Hashids

from app.database import get_db
from app.models import ShortLink
from app.config import Settings

router = APIRouter()
settings = Settings()

# Инициализация Hashids для генерации коротких slug'ов
hashids = Hashids(
    salt=settings.hashids_salt,
    min_length=settings.hashids_min_length
)


class CreateShortLinkRequest(BaseModel):
    """Модель запроса для создания короткой ссылки."""
    target_type: str
    target_id: str


class CreateShortLinkResponse(BaseModel):
    """Модель ответа при создании короткой ссылки."""
    id: int
    slug: str
    url: str


@router.post("/qr/short-links", response_model=CreateShortLinkResponse)
async def create_short_link(
    request: CreateShortLinkRequest,
    db: AsyncSession = Depends(get_db)
) -> CreateShortLinkResponse:
    """
    Создание новой короткой ссылки.
    
    Args:
        request: Данные для создания короткой ссылки
        db: Сессия базы данных
        
    Returns:
        CreateShortLinkResponse: Информация о созданной короткой ссылке
        
    Raises:
        HTTPException: При ошибке создания ссылки
    """
    try:
        # Создание записи в базе данных
        short_link = ShortLink(
            target_type=request.target_type,
            target_id=request.target_id,
            slug="",  # Будет заполнен после сохранения
            active=True
        )
        
        db.add(short_link)
        await db.commit()
        await db.refresh(short_link)
        
        # Генерация slug на основе ID
        slug = hashids.encode(short_link.id)
        short_link.slug = slug
        
        await db.commit()
        await db.refresh(short_link)
        
        return CreateShortLinkResponse(
            id=short_link.id,
            slug=short_link.slug,
            url=f"/r/{short_link.slug}"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create short link: {str(e)}")


@router.get("/qr/{slug}/svg")
async def get_qr_svg(
    slug: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Генерация SVG QR кода для короткой ссылки.
    
    Args:
        slug: Slug короткой ссылки
        db: Сессия базы данных
        
    Returns:
        dict: SVG содержимое QR кода
        
    Raises:
        HTTPException: Если ссылка не найдена или неактивна
    """
    # Поиск короткой ссылки в базе данных
    result = await db.execute(
        select(ShortLink).where(ShortLink.slug == slug)
    )
    short_link = result.scalar_one_or_none()
    
    if not short_link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    if not short_link.active:
        raise HTTPException(status_code=410, detail="Short link is inactive")
    
    # Формирование полного URL для QR кода
    full_url = f"{settings.public_base_url}/r/{slug}"
    
    # Генерация QR кода
    qr = segno.make(full_url, error='M')  # Error level M (Medium)
    svg_content = qr.svg_inline()
    
    return {
        "svg": svg_content,
        "url": full_url,
        "slug": slug
    }