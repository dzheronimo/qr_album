"""
Роуты для работы с макетами печати.
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.layout_service import LayoutService
from app.models.print_models import PrintJobType

router = APIRouter()


class CreateLayoutRequest(BaseModel):
    """Запрос на создание макета печати."""
    name: str = Field(..., min_length=1, max_length=100, description="Название макета")
    description: Optional[str] = Field(None, description="Описание макета")
    layout_type: PrintJobType = Field(..., description="Тип макета")
    page_width: float = Field(..., gt=0, description="Ширина страницы (мм)")
    page_height: float = Field(..., gt=0, description="Высота страницы (мм)")
    margin_top: float = Field(default=10.0, ge=0, description="Верхний отступ (мм)")
    margin_bottom: float = Field(default=10.0, ge=0, description="Нижний отступ (мм)")
    margin_left: float = Field(default=10.0, ge=0, description="Левый отступ (мм)")
    margin_right: float = Field(default=10.0, ge=0, description="Правый отступ (мм)")
    elements: Optional[Dict[str, Any]] = Field(None, description="Элементы макета")
    is_system: bool = Field(default=False, description="Системный макет")


class UpdateLayoutRequest(BaseModel):
    """Запрос на обновление макета печати."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название макета")
    description: Optional[str] = Field(None, description="Описание макета")
    layout_type: Optional[PrintJobType] = Field(None, description="Тип макета")
    page_width: Optional[float] = Field(None, gt=0, description="Ширина страницы (мм)")
    page_height: Optional[float] = Field(None, gt=0, description="Высота страницы (мм)")
    margin_top: Optional[float] = Field(None, ge=0, description="Верхний отступ (мм)")
    margin_bottom: Optional[float] = Field(None, ge=0, description="Нижний отступ (мм)")
    margin_left: Optional[float] = Field(None, ge=0, description="Левый отступ (мм)")
    margin_right: Optional[float] = Field(None, ge=0, description="Правый отступ (мм)")
    elements: Optional[Dict[str, Any]] = Field(None, description="Элементы макета")
    is_active: Optional[bool] = Field(None, description="Активность макета")


class LayoutResponse(BaseModel):
    """Ответ с информацией о макете печати."""
    id: int
    name: str
    description: Optional[str]
    layout_type: str
    page_width: float
    page_height: float
    margin_top: float
    margin_bottom: float
    margin_left: float
    margin_right: float
    elements: Dict[str, Any]
    is_active: bool
    is_system: bool
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class LayoutStatsResponse(BaseModel):
    """Ответ со статистикой макетов."""
    total_layouts: int
    active_layouts: int
    layouts_by_type: Dict[str, int]


@router.post("/layouts", response_model=LayoutResponse, status_code=status.HTTP_201_CREATED)
async def create_layout(
    request: CreateLayoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание макета печати."""
    layout_service = LayoutService(db)
    
    try:
        layout = await layout_service.create_layout(
            name=request.name,
            description=request.description,
            layout_type=request.layout_type,
            page_width=request.page_width,
            page_height=request.page_height,
            margin_top=request.margin_top,
            margin_bottom=request.margin_bottom,
            margin_left=request.margin_left,
            margin_right=request.margin_right,
            elements=request.elements,
            is_system=request.is_system
        )
        
        return LayoutResponse(**layout.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании макета: {str(e)}"
        )


@router.get("/layouts", response_model=List[LayoutResponse])
async def get_layouts(
    layout_type: Optional[PrintJobType] = Query(None, description="Тип макета для фильтрации"),
    is_active: Optional[bool] = Query(None, description="Активность макета"),
    is_system: Optional[bool] = Query(None, description="Системный макет"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка макетов печати."""
    layout_service = LayoutService(db)
    
    try:
        layouts = await layout_service.get_layouts(
            layout_type=layout_type,
            is_active=is_active,
            is_system=is_system,
            skip=skip,
            limit=limit
        )
        
        return [LayoutResponse(**layout.to_dict()) for layout in layouts]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении макетов: {str(e)}"
        )


@router.get("/layouts/active", response_model=List[LayoutResponse])
async def get_active_layouts(
    layout_type: Optional[PrintJobType] = Query(None, description="Тип макета для фильтрации"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение активных макетов печати."""
    layout_service = LayoutService(db)
    
    try:
        layouts = await layout_service.get_active_layouts(
            layout_type=layout_type,
            skip=skip,
            limit=limit
        )
        
        return [LayoutResponse(**layout.to_dict()) for layout in layouts]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении активных макетов: {str(e)}"
        )


@router.get("/layouts/{layout_id}", response_model=LayoutResponse)
async def get_layout(
    layout_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение макета печати по ID."""
    layout_service = LayoutService(db)
    
    layout = await layout_service.get_layout_by_id(layout_id)
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Макет не найден"
        )
    
    return LayoutResponse(**layout.to_dict())


@router.put("/layouts/{layout_id}", response_model=LayoutResponse)
async def update_layout(
    layout_id: int,
    request: UpdateLayoutRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление макета печати."""
    layout_service = LayoutService(db)
    
    try:
        updated_layout = await layout_service.update_layout(
            layout_id=layout_id,
            name=request.name,
            description=request.description,
            layout_type=request.layout_type,
            page_width=request.page_width,
            page_height=request.page_height,
            margin_top=request.margin_top,
            margin_bottom=request.margin_bottom,
            margin_left=request.margin_left,
            margin_right=request.margin_right,
            elements=request.elements,
            is_active=request.is_active
        )
        
        if not updated_layout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Макет не найден"
            )
        
        return LayoutResponse(**updated_layout.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении макета: {str(e)}"
        )


@router.delete("/layouts/{layout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_layout(
    layout_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление макета печати."""
    layout_service = LayoutService(db)
    
    try:
        success = await layout_service.delete_layout(layout_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Макет не найден"
            )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении макета: {str(e)}"
        )


@router.post("/layouts/{layout_id}/toggle", response_model=LayoutResponse)
async def toggle_layout_status(
    layout_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Переключение статуса активности макета."""
    layout_service = LayoutService(db)
    
    try:
        success = await layout_service.toggle_layout_status(layout_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Макет не найден"
            )
        
        # Получаем обновленный макет
        updated_layout = await layout_service.get_layout_by_id(layout_id)
        return LayoutResponse(**updated_layout.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при переключении статуса макета: {str(e)}"
        )


@router.post("/layouts/{layout_id}/validate", status_code=status.HTTP_200_OK)
async def validate_layout(
    layout_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Валидация макета печати."""
    layout_service = LayoutService(db)
    
    layout = await layout_service.get_layout_by_id(layout_id)
    if not layout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Макет не найден"
        )
    
    try:
        is_valid, error_message = await layout_service.validate_layout(layout)
        return {
            "is_valid": is_valid,
            "error_message": error_message
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при валидации макета: {str(e)}"
        )


@router.get("/layouts/stats", response_model=LayoutStatsResponse)
async def get_layout_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики макетов печати."""
    layout_service = LayoutService(db)
    
    try:
        stats = await layout_service.get_layout_stats()
        return LayoutStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики макетов: {str(e)}"
        )
