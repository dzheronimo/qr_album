"""
Роуты для работы с шаблонами печати.
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.template_service import TemplateService
from app.models.print_models import PrintJobType

router = APIRouter()


class CreateTemplateRequest(BaseModel):
    """Запрос на создание шаблона печати."""
    name: str = Field(..., min_length=1, max_length=100, description="Название шаблона")
    description: Optional[str] = Field(None, description="Описание шаблона")
    template_type: PrintJobType = Field(..., description="Тип шаблона")
    html_template: str = Field(..., description="HTML шаблон")
    css_styles: Optional[str] = Field(None, description="CSS стили")
    category: Optional[str] = Field(None, description="Категория шаблона")
    default_page_size: str = Field(default="A4", description="Размер страницы по умолчанию")
    default_orientation: str = Field(default="portrait", description="Ориентация по умолчанию")
    default_quality: int = Field(default=300, ge=72, le=600, description="Качество по умолчанию")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="Переменные шаблона")
    required_fields: Optional[List[str]] = Field(None, description="Обязательные поля")
    is_system: bool = Field(default=False, description="Системный шаблон")


class UpdateTemplateRequest(BaseModel):
    """Запрос на обновление шаблона печати."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название шаблона")
    description: Optional[str] = Field(None, description="Описание шаблона")
    template_type: Optional[PrintJobType] = Field(None, description="Тип шаблона")
    html_template: Optional[str] = Field(None, description="HTML шаблон")
    css_styles: Optional[str] = Field(None, description="CSS стили")
    category: Optional[str] = Field(None, description="Категория шаблона")
    default_page_size: Optional[str] = Field(None, description="Размер страницы по умолчанию")
    default_orientation: Optional[str] = Field(None, description="Ориентация по умолчанию")
    default_quality: Optional[int] = Field(None, ge=72, le=600, description="Качество по умолчанию")
    template_variables: Optional[Dict[str, Any]] = Field(None, description="Переменные шаблона")
    required_fields: Optional[List[str]] = Field(None, description="Обязательные поля")
    is_active: Optional[bool] = Field(None, description="Активность шаблона")


class TemplateResponse(BaseModel):
    """Ответ с информацией о шаблоне печати."""
    id: int
    name: str
    description: Optional[str]
    template_type: str
    category: Optional[str]
    html_template: str
    css_styles: Optional[str]
    default_page_size: str
    default_orientation: str
    default_quality: int
    template_variables: Optional[Dict[str, Any]]
    required_fields: Optional[List[str]]
    is_active: bool
    is_system: bool
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class TemplateStatsResponse(BaseModel):
    """Ответ со статистикой шаблонов."""
    total_templates: int
    active_templates: int
    templates_by_type: Dict[str, int]
    templates_by_category: Dict[str, int]


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: CreateTemplateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание шаблона печати."""
    template_service = TemplateService(db)
    
    try:
        template = await template_service.create_template(
            name=request.name,
            description=request.description,
            template_type=request.template_type,
            html_template=request.html_template,
            css_styles=request.css_styles,
            category=request.category,
            default_page_size=request.default_page_size,
            default_orientation=request.default_orientation,
            default_quality=request.default_quality,
            template_variables=request.template_variables,
            required_fields=request.required_fields,
            is_system=request.is_system
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
    template_type: Optional[PrintJobType] = Query(None, description="Тип шаблона для фильтрации"),
    category: Optional[str] = Query(None, description="Категория для фильтрации"),
    is_active: Optional[bool] = Query(None, description="Активность шаблона"),
    is_system: Optional[bool] = Query(None, description="Системный шаблон"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка шаблонов печати."""
    template_service = TemplateService(db)
    
    try:
        templates = await template_service.get_templates(
            template_type=template_type,
            category=category,
            is_active=is_active,
            is_system=is_system,
            skip=skip,
            limit=limit
        )
        
        return [TemplateResponse(**template.to_dict()) for template in templates]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении шаблонов: {str(e)}"
        )


@router.get("/templates/active", response_model=List[TemplateResponse])
async def get_active_templates(
    template_type: Optional[PrintJobType] = Query(None, description="Тип шаблона для фильтрации"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение активных шаблонов печати."""
    template_service = TemplateService(db)
    
    try:
        templates = await template_service.get_active_templates(
            template_type=template_type,
            skip=skip,
            limit=limit
        )
        
        return [TemplateResponse(**template.to_dict()) for template in templates]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении активных шаблонов: {str(e)}"
        )


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение шаблона печати по ID."""
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
    """Обновление шаблона печати."""
    template_service = TemplateService(db)
    
    try:
        updated_template = await template_service.update_template(
            template_id=template_id,
            name=request.name,
            description=request.description,
            template_type=request.template_type,
            html_template=request.html_template,
            css_styles=request.css_styles,
            category=request.category,
            default_page_size=request.default_page_size,
            default_orientation=request.default_orientation,
            default_quality=request.default_quality,
            template_variables=request.template_variables,
            required_fields=request.required_fields,
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
    """Удаление шаблона печати."""
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


@router.post("/templates/{template_id}/toggle", response_model=TemplateResponse)
async def toggle_template_status(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Переключение статуса активности шаблона."""
    template_service = TemplateService(db)
    
    try:
        success = await template_service.toggle_template_status(template_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаблон не найден"
            )
        
        # Получаем обновленный шаблон
        updated_template = await template_service.get_template_by_id(template_id)
        return TemplateResponse(**updated_template.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при переключении статуса шаблона: {str(e)}"
        )


@router.post("/templates/{template_id}/validate", status_code=status.HTTP_200_OK)
async def validate_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Валидация шаблона печати."""
    template_service = TemplateService(db)
    
    template = await template_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Шаблон не найден"
        )
    
    try:
        is_valid, error_message = await template_service.validate_template(template)
        return {
            "is_valid": is_valid,
            "error_message": error_message
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при валидации шаблона: {str(e)}"
        )


@router.get("/templates/stats", response_model=TemplateStatsResponse)
async def get_template_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики шаблонов печати."""
    template_service = TemplateService(db)
    
    try:
        stats = await template_service.get_template_stats()
        return TemplateStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики шаблонов: {str(e)}"
        )
