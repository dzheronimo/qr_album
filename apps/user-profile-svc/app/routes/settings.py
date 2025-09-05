"""
Роуты для работы с настройками пользователей.
"""

from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.settings_service import SettingsService
from app.models.user_profile import ThemeType, LanguageType

router = APIRouter()


class UpdateSettingsRequest(BaseModel):
    """Запрос на обновление настроек."""
    theme: Optional[ThemeType] = Field(None, description="Тема оформления")
    language: Optional[LanguageType] = Field(None, description="Язык интерфейса")
    email_notifications: Optional[bool] = Field(None, description="Email уведомления")
    push_notifications: Optional[bool] = Field(None, description="Push уведомления")
    sms_notifications: Optional[bool] = Field(None, description="SMS уведомления")
    profile_visibility: Optional[str] = Field(None, description="Видимость профиля")
    album_visibility: Optional[str] = Field(None, description="Видимость альбомов")
    allow_following: Optional[bool] = Field(None, description="Разрешить подписки")
    two_factor_enabled: Optional[bool] = Field(None, description="Двухфакторная аутентификация")
    login_notifications: Optional[bool] = Field(None, description="Уведомления о входе")
    auto_save_drafts: Optional[bool] = Field(None, description="Автосохранение черновиков")
    compress_images: Optional[bool] = Field(None, description="Сжатие изображений")
    max_file_size_mb: Optional[int] = Field(None, ge=1, le=100, description="Максимальный размер файла")
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Пользовательские настройки")


class CustomSettingRequest(BaseModel):
    """Запрос на обновление пользовательской настройки."""
    key: str = Field(..., min_length=1, max_length=100, description="Ключ настройки")
    value: Any = Field(..., description="Значение настройки")


class SettingsResponse(BaseModel):
    """Ответ с настройками пользователя."""
    id: int
    user_id: int
    theme: str
    language: str
    email_notifications: bool
    push_notifications: bool
    sms_notifications: bool
    profile_visibility: str
    album_visibility: str
    allow_following: bool
    two_factor_enabled: bool
    login_notifications: bool
    auto_save_drafts: bool
    compress_images: bool
    max_file_size_mb: int
    custom_settings: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


@router.get("/settings", response_model=SettingsResponse)
async def get_my_settings(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение настроек пользователя."""
    settings_service = SettingsService(db)
    
    settings = await settings_service.get_or_create_settings(user_id)
    return SettingsResponse(**settings.to_dict())


@router.put("/settings", response_model=SettingsResponse)
async def update_my_settings(
    request: UpdateSettingsRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление настроек пользователя."""
    settings_service = SettingsService(db)
    
    settings = await settings_service.update_settings(
        user_id=user_id,
        theme=request.theme,
        language=request.language,
        email_notifications=request.email_notifications,
        push_notifications=request.push_notifications,
        sms_notifications=request.sms_notifications,
        profile_visibility=request.profile_visibility,
        album_visibility=request.album_visibility,
        allow_following=request.allow_following,
        two_factor_enabled=request.two_factor_enabled,
        login_notifications=request.login_notifications,
        auto_save_drafts=request.auto_save_drafts,
        compress_images=request.compress_images,
        max_file_size_mb=request.max_file_size_mb,
        custom_settings=request.custom_settings
    )
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки не найдены"
        )
    
    return SettingsResponse(**settings.to_dict())


@router.put("/settings/custom", response_model=SettingsResponse)
async def update_custom_setting(
    request: CustomSettingRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление пользовательской настройки."""
    settings_service = SettingsService(db)
    
    settings = await settings_service.update_custom_setting(
        user_id=user_id,
        key=request.key,
        value=request.value
    )
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки не найдены"
        )
    
    return SettingsResponse(**settings.to_dict())


@router.get("/settings/custom/{key}")
async def get_custom_setting(
    key: str,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    default: Optional[Any] = Query(None, description="Значение по умолчанию"),
    db: AsyncSession = Depends(get_db)
):
    """Получение пользовательской настройки."""
    settings_service = SettingsService(db)
    
    value = await settings_service.get_custom_setting(
        user_id=user_id,
        key=key,
        default=default
    )
    
    return {"key": key, "value": value}


@router.delete("/settings/custom/{key}", response_model=SettingsResponse)
async def delete_custom_setting(
    key: str,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Удаление пользовательской настройки."""
    settings_service = SettingsService(db)
    
    settings = await settings_service.delete_custom_setting(
        user_id=user_id,
        key=key
    )
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки не найдены"
        )
    
    return SettingsResponse(**settings.to_dict())


@router.post("/settings/reset", response_model=SettingsResponse)
async def reset_settings_to_defaults(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Сброс настроек к значениям по умолчанию."""
    settings_service = SettingsService(db)
    
    settings = await settings_service.reset_to_defaults(user_id)
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки не найдены"
        )
    
    return SettingsResponse(**settings.to_dict())


@router.delete("/settings", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_settings(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Удаление настроек пользователя."""
    settings_service = SettingsService(db)
    
    success = await settings_service.delete_settings(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки не найдены"
        )
