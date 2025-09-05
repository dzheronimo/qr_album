"""
Маршруты для работы с медиафайлами.

Содержит эндпоинты для загрузки и управления медиафайлами через MinIO.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.media_service import MediaService
from app.models.media_file import MediaType, MediaStatus

router = APIRouter()


class InitUploadRequest(BaseModel):
    """Модель запроса для инициализации загрузки."""
    filename: str
    mime_type: str
    file_size: int
    page_id: Optional[int] = None
    album_id: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[str] = None


class InitUploadResponse(BaseModel):
    """Модель ответа при инициализации загрузки."""
    media_id: int
    s3_key: str
    presigned: Dict[str, Any]


class MediaFileResponse(BaseModel):
    """Модель ответа для медиафайла."""
    id: int
    filename: str
    original_filename: str
    user_id: int
    page_id: Optional[int]
    album_id: Optional[int]
    file_type: str
    mime_type: str
    file_size: int
    s3_key: str
    s3_bucket: str
    s3_url: Optional[str]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    status: str
    processing_error: Optional[str]
    tags: Optional[str]
    description: Optional[str]
    created_at: str
    updated_at: str


class UpdateMediaRequest(BaseModel):
    """Модель запроса для обновления медиафайла."""
    description: Optional[str] = None
    tags: Optional[str] = None


@router.post("/media/upload/init", response_model=InitUploadResponse)
async def init_upload(
    request: InitUploadRequest,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Инициализация загрузки медиафайла.
    
    Создает запись о медиафайле и presigned POST для загрузки в MinIO.
    
    Args:
        request: Данные для инициализации загрузки
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        InitUploadResponse: Информация для загрузки файла
        
    Raises:
        HTTPException: При ошибке создания presigned POST
    """
    media_service = MediaService(db)
    
    try:
        # Генерация уникального ключа для файла
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        s3_key = f"uploads/{user_id}/{timestamp}_{request.filename}"
        
        # Создание записи о медиафайле
        media_file = await media_service.create_media_file(
            user_id=user_id,
            filename=request.filename,
            original_filename=request.filename,
            mime_type=request.mime_type,
            file_size=request.file_size,
            s3_key=s3_key,
            page_id=request.page_id,
            album_id=request.album_id,
            description=request.description,
            tags=request.tags
        )
        
        # Создание presigned POST
        presigned_post = media_service.generate_presigned_upload(
            s3_key=s3_key,
            content_type=request.mime_type,
            expires_in=600  # 10 минут
        )
        
        return InitUploadResponse(
            media_id=media_file.id,
            s3_key=s3_key,
            presigned=presigned_post
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/media/{media_id}/confirm")
async def confirm_upload(
    media_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Подтверждение успешной загрузки медиафайла.
    
    Args:
        media_id: ID медиафайла
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат подтверждения
        
    Raises:
        HTTPException: Если медиафайл не найден
    """
    media_service = MediaService(db)
    
    media_file = await media_service.get_media_file_by_id(media_id, user_id)
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиафайл не найден"
        )
    
    # Генерация URL для доступа к файлу
    s3_url = media_service.generate_presigned_download(media_file.s3_key)
    
    # Отметка как готового
    success = await media_service.mark_as_ready(media_id, s3_url)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при подтверждении загрузки"
        )
    
    return {"message": "Загрузка подтверждена", "s3_url": s3_url}


@router.get("/media", response_model=List[MediaFileResponse])
async def get_user_media_files(
    user_id: int,  # TODO: Получать из JWT токена
    file_type: Optional[MediaType] = Query(None, description="Фильтр по типу файла"),
    status: Optional[MediaStatus] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение медиафайлов пользователя.
    
    Args:
        user_id: ID пользователя
        file_type: Фильтр по типу файла
        status: Фильтр по статусу
        limit: Лимит записей
        offset: Смещение
        db: Сессия базы данных
        
    Returns:
        List[MediaFileResponse]: Список медиафайлов пользователя
    """
    media_service = MediaService(db)
    
    media_files = await media_service.get_user_media_files(
        user_id=user_id,
        file_type=file_type,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return [MediaFileResponse(**media_file.to_dict()) for media_file in media_files]


@router.get("/media/page/{page_id}", response_model=List[MediaFileResponse])
async def get_page_media_files(
    page_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    status: Optional[MediaStatus] = Query(None, description="Фильтр по статусу"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение медиафайлов страницы.
    
    Args:
        page_id: ID страницы
        user_id: ID пользователя
        status: Фильтр по статусу
        db: Сессия базы данных
        
    Returns:
        List[MediaFileResponse]: Список медиафайлов страницы
    """
    media_service = MediaService(db)
    
    media_files = await media_service.get_media_files_by_page(
        page_id=page_id,
        user_id=user_id,
        status=status
    )
    
    return [MediaFileResponse(**media_file.to_dict()) for media_file in media_files]


@router.get("/media/album/{album_id}", response_model=List[MediaFileResponse])
async def get_album_media_files(
    album_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    status: Optional[MediaStatus] = Query(None, description="Фильтр по статусу"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение медиафайлов альбома.
    
    Args:
        album_id: ID альбома
        user_id: ID пользователя
        status: Фильтр по статусу
        db: Сессия базы данных
        
    Returns:
        List[MediaFileResponse]: Список медиафайлов альбома
    """
    media_service = MediaService(db)
    
    media_files = await media_service.get_media_files_by_album(
        album_id=album_id,
        user_id=user_id,
        status=status
    )
    
    return [MediaFileResponse(**media_file.to_dict()) for media_file in media_files]


@router.get("/media/{media_id}", response_model=MediaFileResponse)
async def get_media_file(
    media_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Получение медиафайла по ID.
    
    Args:
        media_id: ID медиафайла
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        MediaFileResponse: Медиафайл
        
    Raises:
        HTTPException: Если медиафайл не найден
    """
    media_service = MediaService(db)
    
    media_file = await media_service.get_media_file_by_id(media_id, user_id)
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиафайл не найден"
        )
    
    return MediaFileResponse(**media_file.to_dict())


@router.put("/media/{media_id}", response_model=MediaFileResponse)
async def update_media_file(
    media_id: int,
    request: UpdateMediaRequest,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление медиафайла.
    
    Args:
        media_id: ID медиафайла
        request: Данные для обновления
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        MediaFileResponse: Обновленный медиафайл
        
    Raises:
        HTTPException: Если медиафайл не найден
    """
    media_service = MediaService(db)
    
    media_file = await media_service.update_media_file(
        media_id=media_id,
        user_id=user_id,
        description=request.description,
        tags=request.tags
    )
    
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиафайл не найден"
        )
    
    return MediaFileResponse(**media_file.to_dict())


@router.delete("/media/{media_id}")
async def delete_media_file(
    media_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление медиафайла.
    
    Args:
        media_id: ID медиафайла
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат удаления
        
    Raises:
        HTTPException: Если медиафайл не найден
    """
    media_service = MediaService(db)
    
    success = await media_service.delete_media_file(media_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиафайл не найден"
        )
    
    return {"message": "Медиафайл успешно удален"}


@router.get("/media/{media_id}/download")
async def get_download_url(
    media_id: int,
    user_id: int,  # TODO: Получать из JWT токена
    expires_in: int = Query(3600, ge=60, le=86400, description="Время жизни URL в секундах"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение URL для скачивания медиафайла.
    
    Args:
        media_id: ID медиафайла
        user_id: ID пользователя
        expires_in: Время жизни URL в секундах
        db: Сессия базы данных
        
    Returns:
        dict: URL для скачивания
        
    Raises:
        HTTPException: Если медиафайл не найден
    """
    media_service = MediaService(db)
    
    media_file = await media_service.get_media_file_by_id(media_id, user_id)
    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медиафайл не найден"
        )
    
    try:
        download_url = media_service.generate_presigned_download(
            media_file.s3_key,
            expires_in=expires_in
        )
        
        return {
            "download_url": download_url,
            "expires_in": expires_in,
            "filename": media_file.original_filename
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/media/stats")
async def get_media_stats(
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Получение статистики медиафайлов пользователя.
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Статистика медиафайлов
    """
    media_service = MediaService(db)
    
    stats = await media_service.get_media_stats(user_id)
    return stats
