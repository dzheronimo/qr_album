"""
Роуты для работы с шаблонами уведомлений.
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.template_service import TemplateService
from app.models.notification import NotificationType

router = APIRouter()


class CreateTemplateRequest(BaseModel):
    """Запрос на создание шаблона уведомления."""
    name: str = Field(..., min_length=1, max_length=100, description="Название шаблона")
    notification_type: NotificationType = Field(..., description="Тип уведомления")
    content: str = Field(..., min_length=1, description="Содержимое шаблона")
    subject: Optional[str] = Field(None, max_length=200, description="Тема (для email)")
    variables: Optional[Dict[str, Any]] = Field(None, description="Переменные для подстановки")
    description: Optional[str] = Field(None, description="Описание шаблона")
    category: Optional[str] = Field(None, max_length=50, description="Категория шаблона")


class UpdateTemplateRequest(BaseModel):
    """Запрос на обновление шаблона уведомления."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название шаблона")
    notification_type: Optional[NotificationType] = Field(None, description="Тип уведомления")
    content: Optional[str] = Field(None, min_length=1, description="Содержимое шаблона")
    subject: Optional[str] = Field(None, max_length=200, description="Тема (для email)")
    variables: Optional[Dict[str, Any]] = Field(None, description="Переменные для подстановки")
    description: Optional[str] = Field(None, description="Описание шаблона")
    category: Optional[str] = Field(None, max_length=50, description="Категория шаблона")
    is_active: Optional[bool] = Field(None, description="Активный шаблон")


class RenderTemplateRequest(BaseModel):
    """Запрос на рендеринг шаблона."""
    variables: Dict[str, Any] = Field(..., description="Переменные для подстановки")


class TemplateResponse(BaseModel):
    """Ответ с информацией о шаблоне уведомления."""
    id: int
    name: str
    notification_type: str
    subject: Optional[str]
    content: str
    is_active: bool
    variables: Optional[Dict[str, Any]]
    description: Optional[str]
    category: Optional[str]
    created_at: str
    updated_at: str


class RenderedTemplateResponse(BaseModel):
    """Ответ с рендеренным шаблоном."""
    subject: str
    content: str


class TemplateStatsResponse(BaseModel):
    """Ответ со статистикой шаблонов."""
    total_templates: int
    active_templates: int
    templates_by_type: Dict[str, int]
    top_templates_by_usage: List[Dict[str, Any]]


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание шаблона уведомления."""
    template_service = TemplateService(db)
    
    try:
        template = await template_service.create_template(
            name=request.name,
            notification_type=request.notification_type,
            content=request.content,
            subject=request.subject,
            variables=request.variables,
            description=request.description,
            category=request.category
        )
        
        return TemplateResponse(**template.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании шаблона: {str(e)}"
        )


@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates(
    notification_type: Optional[NotificationType] = Query(None, description="Тип уведомления для фильтрации"),
    category: Optional[str] = Query(None, description="Категория для фильтрации"),
    is_active: bool = Query(True, description="Только активные шаблоны"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка шаблонов уведомлений."""
    template_service = TemplateService(db)
    
    try:
        templates = await template_service.get_templates(
            notification_type=notification_type,
            category=category,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        return [TemplateResponse(**template.to_dict()) for template in templates]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении шаблонов: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение шаблона уведомления по ID."""
    template_service = TemplateService(db)
    
    template = await template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон не найден"
        )
    
    return TemplateResponse(**template.to_dict())


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    request: UpdateTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление шаблона уведомления."""
    template_service = TemplateService(db)
    
    try:
        updated_template = await template_service.update_template(
            template_id=template_id,
            name=request.name,
            notification_type=request.notification_type,
            content=request.content,
            subject=request.subject,
            variables=request.variables,
            description=request.description,
            category=request.category,
            is_active=request.is_active
        )
        
        if not updated_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаблон не найден"
            )
        
        return TemplateResponse(**updated_template.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении шаблона: {str(e)}"
        )


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление шаблона уведомления."""
    template_service = TemplateService(db)
    
    try:
        success = await template_service.delete_template(template_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаблон не найден"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении шаблона: {str(e)}"
        )


@router.post("/templates/{template_id}/render", response_model=RenderedTemplateResponse)
async def render_template(
    template_id: int,
    request: RenderTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Рендеринг шаблона с переменными."""
    template_service = TemplateService(db)
    
    try:
        rendered = await template_service.render_template(
            template_id=template_id,
            variables=request.variables
        )
        
        if not rendered:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаблон не найден"
            )
        
        return RenderedTemplateResponse(**rendered)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при рендеринге шаблона: {str(e)}"
        )


@router.get("/templates/stats", response_model=TemplateStatsResponse)
async def get_template_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики шаблонов уведомлений."""
    template_service = TemplateService(db)
    
    try:
        stats = await template_service.get_template_stats()
        return TemplateStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики шаблонов: {str(e)}"
        )
