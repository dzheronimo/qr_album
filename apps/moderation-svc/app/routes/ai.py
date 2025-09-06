"""
Роуты для работы с AI модерацией.
"""

from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.ai_service import AIService

router = APIRouter()


class AIStatsResponse(BaseModel):
    """Ответ со статистикой AI модерации."""
    total_analyses: int
    analyses_by_type: Dict[str, int]
    average_confidence: float
    average_processing_time_ms: float
    available_models: List[str]


@router.get("/ai/stats", response_model=AIStatsResponse)
async def get_ai_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики AI модерации."""
    ai_service = AIService(db)
    
    try:
        stats = await ai_service.get_ai_stats()
        return AIStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики AI: {str(e)}"
        )
