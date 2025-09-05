"""
Роуты для работы с профилями пользователей.
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.profile_service import ProfileService
from app.models.user_profile import UserProfile

router = APIRouter()


class CreateProfileRequest(BaseModel):
    """Запрос на создание профиля."""
    first_name: Optional[str] = Field(None, max_length=100, description="Имя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия")
    middle_name: Optional[str] = Field(None, max_length=100, description="Отчество")
    display_name: Optional[str] = Field(None, max_length=200, description="Отображаемое имя")
    bio: Optional[str] = Field(None, description="Биография")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    website: Optional[str] = Field(None, max_length=500, description="Веб-сайт")
    location: Optional[str] = Field(None, max_length=200, description="Местоположение")
    timezone: Optional[str] = Field(None, max_length=50, description="Часовой пояс")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL аватара")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="URL обложки")
    social_links: Optional[Dict[str, Any]] = Field(None, description="Ссылки на социальные сети")
    is_public: bool = Field(default=True, description="Публичный профиль")
    show_email: bool = Field(default=False, description="Показывать email")
    show_phone: bool = Field(default=False, description="Показывать телефон")
    show_location: bool = Field(default=False, description="Показывать местоположение")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")


class UpdateProfileRequest(BaseModel):
    """Запрос на обновление профиля."""
    first_name: Optional[str] = Field(None, max_length=100, description="Имя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия")
    middle_name: Optional[str] = Field(None, max_length=100, description="Отчество")
    display_name: Optional[str] = Field(None, max_length=200, description="Отображаемое имя")
    bio: Optional[str] = Field(None, description="Биография")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    website: Optional[str] = Field(None, max_length=500, description="Веб-сайт")
    location: Optional[str] = Field(None, max_length=200, description="Местоположение")
    timezone: Optional[str] = Field(None, max_length=50, description="Часовой пояс")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL аватара")
    cover_image_url: Optional[str] = Field(None, max_length=500, description="URL обложки")
    social_links: Optional[Dict[str, Any]] = Field(None, description="Ссылки на социальные сети")
    is_public: Optional[bool] = Field(None, description="Публичный профиль")
    show_email: Optional[bool] = Field(None, description="Показывать email")
    show_phone: Optional[bool] = Field(None, description="Показывать телефон")
    show_location: Optional[bool] = Field(None, description="Показывать местоположение")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные метаданные")


class ProfileResponse(BaseModel):
    """Ответ с информацией о профиле."""
    id: int
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    display_name: Optional[str]
    bio: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    location: Optional[str]
    timezone: Optional[str]
    avatar_url: Optional[str]
    cover_image_url: Optional[str]
    social_links: Optional[Dict[str, Any]]
    is_public: bool
    show_email: bool
    show_phone: bool
    show_location: bool
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str
    last_seen_at: Optional[str]


class ProfileStatsResponse(BaseModel):
    """Ответ со статистикой профиля."""
    user_id: int
    profile_created_at: str
    last_updated_at: str
    last_seen_at: Optional[str]
    is_public: bool
    has_avatar: bool
    has_cover: bool
    has_bio: bool
    has_social_links: bool


@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    request: CreateProfileRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание профиля пользователя."""
    profile_service = ProfileService(db)
    
    try:
        profile = await profile_service.create_profile(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            middle_name=request.middle_name,
            display_name=request.display_name,
            bio=request.bio,
            phone=request.phone,
            website=request.website,
            location=request.location,
            timezone=request.timezone,
            avatar_url=request.avatar_url,
            cover_image_url=request.cover_image_url,
            social_links=request.social_links,
            is_public=request.is_public,
            show_email=request.show_email,
            show_phone=request.show_phone,
            show_location=request.show_location,
            extra_data=request.extra_data
        )
        
        return ProfileResponse(**profile.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании профиля: {str(e)}"
        )


@router.get("/profiles/me", response_model=ProfileResponse)
async def get_my_profile(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение собственного профиля."""
    profile_service = ProfileService(db)
    
    profile = await profile_service.get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    
    return ProfileResponse(**profile.to_dict())


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение профиля по ID."""
    profile_service = ProfileService(db)
    
    profile = await profile_service.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    
    return ProfileResponse(**profile.to_dict())


@router.get("/profiles", response_model=List[ProfileResponse])
async def get_public_profiles(
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка публичных профилей."""
    profile_service = ProfileService(db)
    
    try:
        profiles = await profile_service.get_public_profiles(
            skip=skip,
            limit=limit,
            search=search
        )
        
        return [ProfileResponse(**profile.to_dict()) for profile in profiles]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении профилей: {str(e)}"
        )


@router.put("/profiles/me", response_model=ProfileResponse)
async def update_my_profile(
    request: UpdateProfileRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление собственного профиля."""
    profile_service = ProfileService(db)
    
    profile = await profile_service.update_profile(
        user_id=user_id,
        first_name=request.first_name,
        last_name=request.last_name,
        middle_name=request.middle_name,
        display_name=request.display_name,
        bio=request.bio,
        phone=request.phone,
        website=request.website,
        location=request.location,
        timezone=request.timezone,
        avatar_url=request.avatar_url,
        cover_image_url=request.cover_image_url,
        social_links=request.social_links,
        is_public=request.is_public,
        show_email=request.show_email,
        show_phone=request.show_phone,
        show_location=request.show_location,
        extra_data=request.extra_data
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    
    return ProfileResponse(**profile.to_dict())


@router.delete("/profiles/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_profile(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Удаление собственного профиля."""
    profile_service = ProfileService(db)
    
    success = await profile_service.delete_profile(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )


@router.post("/profiles/me/last-seen")
async def update_last_seen(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обновление времени последнего посещения."""
    profile_service = ProfileService(db)
    
    success = await profile_service.update_last_seen(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    
    return {"message": "Время последнего посещения обновлено"}


@router.get("/profiles/me/stats", response_model=ProfileStatsResponse)
async def get_my_profile_stats(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики собственного профиля."""
    profile_service = ProfileService(db)
    
    stats = await profile_service.get_profile_stats(user_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль не найден"
        )
    
    return ProfileStatsResponse(**stats)
