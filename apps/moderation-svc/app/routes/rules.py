"""
Роуты для работы с правилами модерации.
"""

from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.rule_service import RuleService
from app.models.moderation import ContentType

router = APIRouter()


class CreateRuleRequest(BaseModel):
    """Запрос на создание правила модерации."""
    name: str = Field(..., min_length=1, max_length=100, description="Название правила")
    description: Optional[str] = Field(None, description="Описание правила")
    content_type: ContentType = Field(..., description="Тип контента")
    conditions: Dict[str, Any] = Field(..., description="Условия правила")
    action: str = Field(..., description="Действие при срабатывании")
    threshold: Optional[float] = Field(None, description="Пороговое значение")
    priority: int = Field(default=1, ge=1, le=10, description="Приоритет правила")
    auto_action: bool = Field(default=False, description="Автоматическое действие")


class UpdateRuleRequest(BaseModel):
    """Запрос на обновление правила модерации."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название правила")
    description: Optional[str] = Field(None, description="Описание правила")
    content_type: Optional[ContentType] = Field(None, description="Тип контента")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Условия правила")
    action: Optional[str] = Field(None, description="Действие при срабатывании")
    threshold: Optional[float] = Field(None, description="Пороговое значение")
    priority: Optional[int] = Field(None, ge=1, le=10, description="Приоритет правила")
    is_active: Optional[bool] = Field(None, description="Активность правила")
    auto_action: Optional[bool] = Field(None, description="Автоматическое действие")


class RuleResponse(BaseModel):
    """Ответ с информацией о правиле модерации."""
    id: int
    name: str
    description: Optional[str]
    content_type: str
    is_active: bool
    priority: int
    conditions: Dict[str, Any]
    threshold: Optional[float]
    action: str
    auto_action: bool
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class RuleStatsResponse(BaseModel):
    """Ответ со статистикой правил."""
    total_rules: int
    active_rules: int
    rules_by_content_type: Dict[str, int]
    rules_by_action: Dict[str, int]


@router.post("/rules", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    request: CreateRuleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание правила модерации."""
    rule_service = RuleService(db)
    
    try:
        rule = await rule_service.create_rule(
            name=request.name,
            description=request.description,
            content_type=request.content_type,
            conditions=request.conditions,
            action=request.action,
            threshold=request.threshold,
            priority=request.priority,
            auto_action=request.auto_action
        )
        
        return RuleResponse(**rule.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании правила: {str(e)}"
        )


@router.get("/rules", response_model=List[RuleResponse])
async def get_rules(
    content_type: Optional[ContentType] = Query(None, description="Тип контента для фильтрации"),
    is_active: Optional[bool] = Query(None, description="Активность правила"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка правил модерации."""
    rule_service = RuleService(db)
    
    try:
        rules = await rule_service.get_all_rules(
            content_type=content_type,
            is_active=is_active,
            skip=skip,
            limit=limit
        )
        
        return [RuleResponse(**rule.to_dict()) for rule in rules]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении правил: {str(e)}"
        )


@router.get("/rules/active", response_model=List[RuleResponse])
async def get_active_rules(
    content_type: Optional[ContentType] = Query(None, description="Тип контента для фильтрации"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение активных правил модерации."""
    rule_service = RuleService(db)
    
    try:
        rules = await rule_service.get_active_rules(
            content_type=content_type,
            skip=skip,
            limit=limit
        )
        
        return [RuleResponse(**rule.to_dict()) for rule in rules]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении активных правил: {str(e)}"
        )


@router.get("/rules/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение правила модерации по ID."""
    rule_service = RuleService(db)
    
    rule = await rule_service.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Правило не найдено"
        )
    
    return RuleResponse(**rule.to_dict())


@router.put("/rules/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    request: UpdateRuleRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление правила модерации."""
    rule_service = RuleService(db)
    
    try:
        updated_rule = await rule_service.update_rule(
            rule_id=rule_id,
            name=request.name,
            description=request.description,
            content_type=request.content_type,
            conditions=request.conditions,
            action=request.action,
            threshold=request.threshold,
            priority=request.priority,
            is_active=request.is_active,
            auto_action=request.auto_action
        )
        
        if not updated_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Правило не найдено"
            )
        
        return RuleResponse(**updated_rule.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении правила: {str(e)}"
        )


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление правила модерации."""
    rule_service = RuleService(db)
    
    try:
        success = await rule_service.delete_rule(rule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Правило не найдено"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении правила: {str(e)}"
        )


@router.post("/rules/{rule_id}/toggle", response_model=RuleResponse)
async def toggle_rule_status(
    rule_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Переключение статуса активности правила."""
    rule_service = RuleService(db)
    
    try:
        success = await rule_service.toggle_rule_status(rule_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Правило не найдено"
            )
        
        # Получаем обновленное правило
        updated_rule = await rule_service.get_rule_by_id(rule_id)
        return RuleResponse(**updated_rule.to_dict())
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при переключении статуса правила: {str(e)}"
        )


@router.get("/rules/stats", response_model=RuleStatsResponse)
async def get_rule_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики правил модерации."""
    rule_service = RuleService(db)
    
    try:
        stats = await rule_service.get_rule_stats()
        return RuleStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики правил: {str(e)}"
        )
