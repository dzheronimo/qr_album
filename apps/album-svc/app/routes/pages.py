"""
Маршруты для работы со страницами альбомов.

Содержит эндпоинты для создания, получения, обновления и удаления страниц.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.page_service import PageService
from app.models.album import PageStatus
from app.dependencies import get_current_user_id

router = APIRouter()


class CreatePageRequest(BaseModel):
    """Модель запроса для создания страницы."""
    title: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = None


class UpdatePageRequest(BaseModel):
    """Модель запроса для обновления страницы."""
    title: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    font_family: Optional[str] = None
    font_size: Optional[int] = None


class ReorderPagesRequest(BaseModel):
    """Модель запроса для изменения порядка страниц."""
    page_orders: List[dict]  # [{"page_id": 1, "order_index": 0}, ...]


class PageResponse(BaseModel):
    """Модель ответа для страницы."""
    id: int
    title: Optional[str]
    content: Optional[str]
    album_id: int
    order_index: int
    status: str
    background_color: Optional[str]
    text_color: Optional[str]
    font_family: Optional[str]
    font_size: Optional[int]
    created_at: str
    updated_at: str


@router.post("/albums/{album_id}/pages", response_model=PageResponse)
async def create_page(
    album_id: int,
    request: CreatePageRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Создание новой страницы в альбоме.
    
    Args:
        album_id: ID альбома
        request: Данные для создания страницы
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        PageResponse: Созданная страница
        
    Raises:
        HTTPException: При ошибке создания страницы
    """
    page_service = PageService(db)
    
    try:
        page = await page_service.create_page(
            album_id=album_id,
            user_id=user_id,
            title=request.title,
            content=request.content,
            order_index=request.order_index
        )
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Альбом не найден или нет доступа"
            )
        
        return PageResponse(**page.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/albums/{album_id}/pages", response_model=List[PageResponse])
async def get_album_pages(
    album_id: int,
    user_id: int = Depends(get_current_user_id),
    status: Optional[PageStatus] = Query(None, description="Фильтр по статусу"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение страниц альбома.
    
    Args:
        album_id: ID альбома
        user_id: ID пользователя
        status: Фильтр по статусу
        db: Сессия базы данных
        
    Returns:
        List[PageResponse]: Список страниц альбома
    """
    page_service = PageService(db)
    
    pages = await page_service.get_album_pages(
        album_id=album_id,
        user_id=user_id,
        status=status
    )
    
    return [PageResponse(**page.to_dict()) for page in pages]


@router.get("/pages/{page_id}", response_model=PageResponse)
async def get_page(
    page_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Получение страницы по ID.
    
    Args:
        page_id: ID страницы
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        PageResponse: Страница
        
    Raises:
        HTTPException: Если страница не найдена
    """
    page_service = PageService(db)
    
    page = await page_service.get_page_by_id(page_id, user_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    
    return PageResponse(**page.to_dict())


@router.put("/pages/{page_id}", response_model=PageResponse)
async def update_page(
    page_id: int,
    request: UpdatePageRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление страницы.
    
    Args:
        page_id: ID страницы
        request: Данные для обновления
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        PageResponse: Обновленная страница
        
    Raises:
        HTTPException: Если страница не найдена
    """
    page_service = PageService(db)
    
    page = await page_service.update_page(
        page_id=page_id,
        user_id=user_id,
        title=request.title,
        content=request.content,
        order_index=request.order_index,
        background_color=request.background_color,
        text_color=request.text_color,
        font_family=request.font_family,
        font_size=request.font_size
    )
    
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    
    return PageResponse(**page.to_dict())


@router.post("/pages/{page_id}/publish")
async def publish_page(
    page_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Публикация страницы.
    
    Args:
        page_id: ID страницы
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат публикации
        
    Raises:
        HTTPException: Если страница не найдена
    """
    page_service = PageService(db)
    
    success = await page_service.publish_page(page_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    
    return {"message": "Страница успешно опубликована"}


@router.post("/pages/{page_id}/archive")
async def archive_page(
    page_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Архивирование страницы.
    
    Args:
        page_id: ID страницы
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат архивирования
        
    Raises:
        HTTPException: Если страница не найдена
    """
    page_service = PageService(db)
    
    success = await page_service.archive_page(page_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    
    return {"message": "Страница успешно архивирована"}


@router.delete("/pages/{page_id}")
async def delete_page(
    page_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Удаление страницы.
    
    Args:
        page_id: ID страницы
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат удаления
        
    Raises:
        HTTPException: Если страница не найдена
    """
    page_service = PageService(db)
    
    success = await page_service.delete_page(page_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Страница не найдена"
        )
    
    return {"message": "Страница успешно удалена"}


@router.post("/albums/{album_id}/pages/reorder")
async def reorder_pages(
    album_id: int,
    request: ReorderPagesRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Изменение порядка страниц в альбоме.
    
    Args:
        album_id: ID альбома
        request: Данные для изменения порядка
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат изменения порядка
        
    Raises:
        HTTPException: При ошибке изменения порядка
    """
    page_service = PageService(db)
    
    success = await page_service.reorder_pages(
        album_id=album_id,
        user_id=user_id,
        page_orders=request.page_orders
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Альбом не найден или нет доступа"
        )
    
    return {"message": "Порядок страниц успешно изменен"}
