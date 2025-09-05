"""
Роуты для работы с QR кодами.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.qr_service import QRService
from app.models.qr_code import QRCodeStatus, QRCodeType
from app.config import Settings

router = APIRouter()


class CreateQRCodeRequest(BaseModel):
    """Запрос на создание QR кода."""
    name: str = Field(..., min_length=1, max_length=255, description="Название QR кода")
    description: Optional[str] = Field(None, description="Описание QR кода")
    qr_type: QRCodeType = Field(..., description="Тип QR кода")
    page_id: Optional[int] = Field(None, description="ID страницы (если тип PAGE)")
    album_id: Optional[int] = Field(None, description="ID альбома (если тип ALBUM)")
    custom_url: Optional[str] = Field(None, max_length=500, description="Кастомная ссылка (если тип CUSTOM)")
    foreground_color: str = Field(default="#000000", pattern="^#[0-9A-Fa-f]{6}$", description="Цвет переднего плана")
    background_color: str = Field(default="#FFFFFF", pattern="^#[0-9A-Fa-f]{6}$", description="Цвет фона")
    logo_url: Optional[str] = Field(None, max_length=500, description="URL логотипа")
    size: int = Field(default=200, ge=50, le=1000, description="Размер QR кода")
    expires_at: Optional[datetime] = Field(None, description="Время истечения")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")


class UpdateQRCodeRequest(BaseModel):
    """Запрос на обновление QR кода."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название QR кода")
    description: Optional[str] = Field(None, description="Описание QR кода")
    foreground_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Цвет переднего плана")
    background_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Цвет фона")
    logo_url: Optional[str] = Field(None, max_length=500, description="URL логотипа")
    size: Optional[int] = Field(None, ge=50, le=1000, description="Размер QR кода")
    status: Optional[QRCodeStatus] = Field(None, description="Статус QR кода")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")


class QRCodeResponse(BaseModel):
    """Ответ с информацией о QR коде."""
    id: int
    name: str
    description: Optional[str]
    qr_type: str
    status: str
    page_id: Optional[int]
    album_id: Optional[int]
    custom_url: Optional[str]
    user_id: int
    qr_data: str
    qr_image_url: Optional[str]
    foreground_color: Optional[str]
    background_color: Optional[str]
    logo_url: Optional[str]
    size: Optional[int]
    scan_count: int
    last_scan_at: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    expires_at: Optional[str]


class QRCodeStatsResponse(BaseModel):
    """Ответ со статистикой QR кода."""
    qr_code_id: int
    total_scans: int
    last_scan_at: Optional[str]
    daily_stats: List[Dict[str, Any]]
    country_stats: List[Dict[str, Any]]
    device_stats: List[Dict[str, Any]]


@router.post("/qr-codes", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_qr_code(
    request: CreateQRCodeRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание нового QR кода."""
    settings = Settings()
    qr_service = QRService(db, settings)
    
    try:
        qr_code = await qr_service.create_qr_code(
            name=request.name,
            qr_type=request.qr_type,
            user_id=user_id,
            page_id=request.page_id,
            album_id=request.album_id,
            custom_url=request.custom_url,
            description=request.description,
            foreground_color=request.foreground_color,
            background_color=request.background_color,
            logo_url=request.logo_url,
            size=request.size,
            expires_at=request.expires_at,
            extra_data=request.extra_data
        )
        
        return QRCodeResponse(**qr_code.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании QR кода: {str(e)}"
        )


@router.get("/qr-codes", response_model=List[QRCodeResponse])
async def get_qr_codes(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    qr_type: Optional[QRCodeType] = Query(None, description="Фильтр по типу QR кода"),
    status: Optional[QRCodeStatus] = Query(None, description="Фильтр по статусу"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка QR кодов пользователя."""
    settings = Settings()
    qr_service = QRService(db, settings)
    
    try:
        qr_codes = await qr_service.get_qr_codes(
            user_id=user_id,
            skip=skip,
            limit=limit,
            qr_type=qr_type,
            status=status
        )
        
        return [QRCodeResponse(**qr_code.to_dict()) for qr_code in qr_codes]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении QR кодов: {str(e)}"
        )


@router.get("/qr-codes/{qr_code_id}", response_model=QRCodeResponse)
async def get_qr_code(
    qr_code_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение QR кода по ID."""
    settings = Settings()
    qr_service = QRService(db, settings)
    
    qr_code = await qr_service.get_qr_code(qr_code_id, user_id)
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR код не найден"
        )
    
    return QRCodeResponse(**qr_code.to_dict())


@router.put("/qr-codes/{qr_code_id}", response_model=QRCodeResponse)
async def update_qr_code(
    qr_code_id: int,
    request: UpdateQRCodeRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление QR кода."""
    settings = Settings()
    qr_service = QRService(db, settings)
    
    qr_code = await qr_service.update_qr_code(
        qr_code_id=qr_code_id,
        user_id=user_id,
        name=request.name,
        description=request.description,
        foreground_color=request.foreground_color,
        background_color=request.background_color,
        logo_url=request.logo_url,
        size=request.size,
        status=request.status,
        extra_data=request.extra_data
    )
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR код не найден"
        )
    
    return QRCodeResponse(**qr_code.to_dict())


@router.delete("/qr-codes/{qr_code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qr_code(
    qr_code_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Удаление QR кода."""
    settings = Settings()
    qr_service = QRService(db, settings)
    
    success = await qr_service.delete_qr_code(qr_code_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR код не найден"
        )


@router.get("/qr-codes/{qr_code_id}/stats", response_model=QRCodeStatsResponse)
async def get_qr_code_stats(
    qr_code_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики QR кода."""
    settings = Settings()
    qr_service = QRService(db, settings)
    
    stats = await qr_service.get_qr_code_stats(qr_code_id, user_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR код не найден"
        )
    
    return QRCodeStatsResponse(**stats)


@router.post("/qr-codes/{qr_code_id}/scan")
async def record_qr_scan(
    qr_code_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Запись сканирования QR кода."""
    settings = Settings()
    qr_service = QRService(db, settings)
    
    # Получаем информацию о запросе
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referer = request.headers.get("referer")
    
    # TODO: Добавить определение геолокации и устройства
    # Пока используем заглушки
    country = None
    city = None
    latitude = None
    longitude = None
    device_type = None
    browser = None
    os = None
    
    try:
        scan = await qr_service.record_scan(
            qr_code_id=qr_code_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            country=country,
            city=city,
            latitude=latitude,
            longitude=longitude,
            device_type=device_type,
            browser=browser,
            os=os
        )
        
        return {"message": "Сканирование записано", "scan_id": scan.id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при записи сканирования: {str(e)}"
        )
