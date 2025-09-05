"""
Маршруты для работы с альбомами.

Содержит эндпоинты для создания, получения, обновления и удаления альбомов.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.album_service import AlbumService
from app.models.album import AlbumStatus

router = APIRouter()


class CreateAlbumRequest(BaseModel):
    """Модель запроса для создания альбома."""
    title: str
    description: Optional[str] = None
    is_public: bool = False
    tags: Optional[str] = None


class UpdateAlbumRequest(BaseModel):
    """Модель запроса для обновления альбома."""
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[str] = None
    cover_image_url: Optional[str] = None


class AlbumResponse(BaseModel):
    """Модель ответа для альбома."""
    id: int
    title: str
    description: Optional[str]
    user_id: int
    status: str
    is_public: bool
    cover_image_url: Optional[str]
    tags: Optional[str]
    created_at: str
    updated_at: str
    published_at: Optional[str]
    pages_count: int


@router.post("/albums", response_model=AlbumResponse)
async def create_album(
    request: CreateAlbumRequest,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Создание нового альбома.
    
    Args:
        request: Данные для создания альбома
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        AlbumResponse: Созданный альбом
        
    Raises:
        HTTPException: При ошибке создания альбома
    """
    album_service = AlbumService(db)
    
    try:
        album = await album_service.create_album(
            user_id=user_id,
            title=request.title,
            description=request.description,
            is_public=request.is_public,
            tags=request.tags
        )
        return AlbumResponse(**album.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/albums", response_model=List[AlbumResponse])
async def get_user_albums(
    user_id: int,  # TODO: Получать из JWT токена
    status: Optional[AlbumStatus] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение альбомов пользователя.
    
    Args:
        user_id: ID пользователя
        status: Фильтр по статусу
        limit: Лимит записей
        offset: Смещение
        db: Сессия базы данных
        
    Returns:
        List[AlbumResponse]: Список альбомов пользователя
    """
    album_service = AlbumService(db)
    
    albums = await album_service.get_user_albums(
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return [AlbumResponse(**album.to_dict()) for album in albums]


@router.get("/albums/public", response_model=List[AlbumResponse])
async def get_public_albums(
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение публичных альбомов.
    
    Args:
        limit: Лимит записей
        offset: Смещение
        db: Сессия базы данных
        
    Returns:
        List[AlbumResponse]: Список публичных альбомов
    """
    album_service = AlbumService(db)
    
    albums = await album_service.get_public_albums(
        limit=limit,
        offset=offset
    )
    
    return [AlbumResponse(**album.to_dict()) for album in albums]


@router.get("/albums/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Получение альбома по ID.
    
    Args:
        album_id: ID альбома
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        AlbumResponse: Альбом
        
    Raises:
        HTTPException: Если альбом не найден
    """
    album_service = AlbumService(db)
    
    album = await album_service.get_album_by_id(album_id, user_id)
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Альбом не найден"
        )
    
    return AlbumResponse(**album.to_dict())


@router.put("/albums/{album_id}", response_model=AlbumResponse)
async def update_album(
    album_id: int,
    request: UpdateAlbumRequest,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление альбома.
    
    Args:
        album_id: ID альбома
        request: Данные для обновления
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        AlbumResponse: Обновленный альбом
        
    Raises:
        HTTPException: Если альбом не найден
    """
    album_service = AlbumService(db)
    
    album = await album_service.update_album(
        album_id=album_id,
        user_id=user_id,
        title=request.title,
        description=request.description,
        is_public=request.is_public,
        tags=request.tags,
        cover_image_url=request.cover_image_url
    )
    
    if not album:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Альбом не найден"
        )
    
    return AlbumResponse(**album.to_dict())


@router.post("/albums/{album_id}/publish")
async def publish_album(
    album_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Публикация альбома.
    
    Args:
        album_id: ID альбома
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат публикации
        
    Raises:
        HTTPException: Если альбом не найден
    """
    album_service = AlbumService(db)
    
    success = await album_service.publish_album(album_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Альбом не найден"
        )
    
    return {"message": "Альбом успешно опубликован"}


@router.post("/albums/{album_id}/archive")
async def archive_album(
    album_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Архивирование альбома.
    
    Args:
        album_id: ID альбома
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат архивирования
        
    Raises:
        HTTPException: Если альбом не найден
    """
    album_service = AlbumService(db)
    
    success = await album_service.archive_album(album_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Альбом не найден"
        )
    
    return {"message": "Альбом успешно архивирован"}


@router.delete("/albums/{album_id}")
async def delete_album(
    album_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление альбома.
    
    Args:
        album_id: ID альбома
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат удаления
        
    Raises:
        HTTPException: Если альбом не найден
    """
    album_service = AlbumService(db)
    
    success = await album_service.delete_album(album_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Альбом не найден"
        )
    
    return {"message": "Альбом успешно удален"}


@router.get("/albums/{album_id}/stats")
async def get_album_stats(
    album_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статистики альбома.
    
    Args:
        album_id: ID альбома
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Статистика альбома
        
    Raises:
        HTTPException: Если альбом не найден
    """
    album_service = AlbumService(db)
    
    stats = await album_service.get_album_stats(album_id, user_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Альбом не найден"
        )
    
    return stats