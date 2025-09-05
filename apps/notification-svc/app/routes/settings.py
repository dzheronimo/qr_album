"""
Роуты для работы с настройками уведомлений.
"""

from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.settings_service import SettingsService

router = APIRouter()


class CreateSettingsRequest(BaseModel):
    """Запрос на создание настроек уведомлений."""
    email_enabled: bool = Field(default=True, description="Включены ли email уведомления")
    push_enabled: bool = Field(default=True, description="Включены ли push уведомления")
    sms_enabled: bool = Field(default=False, description="Включены ли SMS уведомления")
    in_app_enabled: bool = Field(default=True, description="Включены ли внутриприложенные уведомления")
    marketing_emails: bool = Field(default=False, description="Включены ли маркетинговые письма")
    system_notifications: bool = Field(default=True, description="Включены ли системные уведомления")
    security_alerts: bool = Field(default=True, description="Включены ли уведомления безопасности")
    billing_notifications: bool = Field(default=True, description="Включены ли уведомления о биллинге")
    quiet_hours_start: Optional[str] = Field(None, description="Начало тихих часов (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Конец тихих часов (HH:MM)")
    timezone: Optional[str] = Field(None, description="Часовой пояс")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class UpdateSettingsRequest(BaseModel):
    """Запрос на обновление настроек уведомлений."""
    email_enabled: Optional[bool] = Field(None, description="Включены ли email уведомления")
    push_enabled: Optional[bool] = Field(None, description="Включены ли push уведомления")
    sms_enabled: Optional[bool] = Field(None, description="Включены ли SMS уведомления")
    in_app_enabled: Optional[bool] = Field(None, description="Включены ли внутриприложенные уведомления")
    marketing_emails: Optional[bool] = Field(None, description="Включены ли маркетинговые письма")
    system_notifications: Optional[bool] = Field(None, description="Включены ли системные уведомления")
    security_alerts: Optional[bool] = Field(None, description="Включены ли уведомления безопасности")
    billing_notifications: Optional[bool] = Field(None, description="Включены ли уведомления о биллинге")
    quiet_hours_start: Optional[str] = Field(None, description="Начало тихих часов (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Конец тихих часов (HH:MM)")
    timezone: Optional[str] = Field(None, description="Часовой пояс")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class SettingsResponse(BaseModel):
    """Ответ с настройками уведомлений."""
    id: int
    user_id: int
    email_enabled: bool
    push_enabled: bool
    sms_enabled: bool
    in_app_enabled: bool
    marketing_emails: bool
    system_notifications: bool
    security_alerts: bool
    billing_notifications: bool
    quiet_hours_start: Optional[str]
    quiet_hours_end: Optional[str]
    timezone: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class SettingsStatsResponse(BaseModel):
    """Ответ со статистикой настроек уведомлений."""
    total_users_with_settings: int
    email_enabled: int
    push_enabled: int
    sms_enabled: int
    marketing_enabled: int


@router.get("/settings", response_model=SettingsResponse)
async def get_my_settings(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение настроек уведомлений пользователя."""
    settings_service = SettingsService(db)
    
    settings = await settings_service.get_user_settings(user_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки уведомлений не найдены"
        )
    
    return SettingsResponse(**settings.to_dict())


@router.post("/settings", response_model=SettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_settings(
    request: CreateSettingsRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание настроек уведомлений для пользователя."""
    settings_service = SettingsService(db)
    
    try:
        settings = await settings_service.create_user_settings(
            user_id=user_id,
            email_enabled=request.email_enabled,
            push_enabled=request.push_enabled,
            sms_enabled=request.sms_enabled,
            in_app_enabled=request.in_app_enabled,
            marketing_emails=request.marketing_emails,
            system_notifications=request.system_notifications,
            security_alerts=request.security_alerts,
            billing_notifications=request.billing_notifications,
            quiet_hours_start=request.quiet_hours_start,
            quiet_hours_end=request.quiet_hours_end,
            timezone=request.timezone,
            extra_data=request.extra_data
        )
        
        return SettingsResponse(**settings.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании настроек: {str(e)}"
        )


@router.put("/settings", response_model=SettingsResponse)
async def update_settings(
    request: UpdateSettingsRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление настроек уведомлений пользователя."""
    settings_service = SettingsService(db)
    
    try:
        updated_settings = await settings_service.update_user_settings(
            user_id=user_id,
            email_enabled=request.email_enabled,
            push_enabled=request.push_enabled,
            sms_enabled=request.sms_enabled,
            in_app_enabled=request.in_app_enabled,
            marketing_emails=request.marketing_emails,
            system_notifications=request.system_notifications,
            security_alerts=request.security_alerts,
            billing_notifications=request.billing_notifications,
            quiet_hours_start=request.quiet_hours_start,
            quiet_hours_end=request.quiet_hours_end,
            timezone=request.timezone,
            extra_data=request.extra_data
        )
        
        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Настройки уведомлений не найдены"
            )
        
        return SettingsResponse(**updated_settings.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении настроек: {str(e)}"
        )


@router.delete("/settings", status_code=status.HTTP_204_NO_CONTENT)
async def delete_settings(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Удаление настроек уведомлений пользователя."""
    settings_service = SettingsService(db)
    
    try:
        success = await settings_service.delete_user_settings(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Настройки уведомлений не найдены"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении настроек: {str(e)}"
        )


@router.post("/settings/reset", response_model=SettingsResponse)
async def reset_settings(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Сброс настроек уведомлений пользователя к значениям по умолчанию."""
    settings_service = SettingsService(db)
    
    try:
        reset_settings = await settings_service.reset_user_settings(user_id)
        if not reset_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Настройки уведомлений не найдены"
            )
        
        return SettingsResponse(**reset_settings.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сбросе настроек: {str(e)}"
        )


@router.get("/settings/check", status_code=status.HTTP_200_OK)
async def check_notification_permission(
    notification_type: str = Query(..., description="Тип уведомления"),
    category: Optional[str] = Query(None, description="Категория уведомления"),
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Проверка, можно ли отправить уведомление пользователю."""
    settings_service = SettingsService(db)
    
    try:
        can_send = await settings_service.can_send_notification(
            user_id=user_id,
            notification_type=notification_type,
            category=category
        )
        
        return {
            "can_send": can_send,
            "notification_type": notification_type,
            "category": category,
            "user_id": user_id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при проверке разрешения: {str(e)}"
        )


@router.get("/settings/stats", response_model=SettingsStatsResponse)
async def get_settings_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики настроек уведомлений."""
    settings_service = SettingsService(db)
    
    try:
        stats = await settings_service.get_settings_stats()
        return SettingsStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики настроек: {str(e)}"
        )
