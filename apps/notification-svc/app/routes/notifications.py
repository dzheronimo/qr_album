"""
Роуты для работы с уведомлениями.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationPriority

router = APIRouter()


class CreateNotificationRequest(BaseModel):
    """Запрос на создание уведомления."""
    notification_type: NotificationType = Field(..., description="Тип уведомления")
    content: str = Field(..., min_length=1, description="Содержимое уведомления")
    subject: Optional[str] = Field(None, description="Тема (для email)")
    template_id: Optional[int] = Field(None, description="ID шаблона")
    recipient_email: Optional[str] = Field(None, description="Email получателя")
    recipient_phone: Optional[str] = Field(None, description="Телефон получателя")
    recipient_device_token: Optional[str] = Field(None, description="Токен устройства для push")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="Приоритет уведомления")
    scheduled_at: Optional[datetime] = Field(None, description="Время отправки")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class CreateNotificationFromTemplateRequest(BaseModel):
    """Запрос на создание уведомления из шаблона."""
    template_name: str = Field(..., min_length=1, description="Имя шаблона")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Переменные для подстановки")
    recipient_email: Optional[str] = Field(None, description="Email получателя")
    recipient_phone: Optional[str] = Field(None, description="Телефон получателя")
    recipient_device_token: Optional[str] = Field(None, description="Токен устройства для push")
    priority: NotificationPriority = Field(default=NotificationPriority.NORMAL, description="Приоритет уведомления")
    scheduled_at: Optional[datetime] = Field(None, description="Время отправки")


class NotificationResponse(BaseModel):
    """Ответ с информацией об уведомлении."""
    id: int
    user_id: int
    template_id: Optional[int]
    template: Optional[Dict[str, Any]]
    notification_type: str
    subject: Optional[str]
    content: str
    recipient_email: Optional[str]
    recipient_phone: Optional[str]
    recipient_device_token: Optional[str]
    status: str
    priority: str
    scheduled_at: Optional[str]
    sent_at: Optional[str]
    delivered_at: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: str
    updated_at: str


class NotificationStatsResponse(BaseModel):
    """Ответ со статистикой уведомлений."""
    user_id: int
    total_notifications: int
    notifications_by_status: Dict[str, int]
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]


@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    request: CreateNotificationRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание уведомления."""
    notification_service = NotificationService(db)
    
    try:
        notification = await notification_service.create_notification(
            user_id=user_id,
            notification_type=request.notification_type,
            content=request.content,
            subject=request.subject,
            template_id=request.template_id,
            recipient_email=request.recipient_email,
            recipient_phone=request.recipient_phone,
            recipient_device_token=request.recipient_device_token,
            priority=request.priority,
            scheduled_at=request.scheduled_at,
            extra_data=request.extra_data
        )
        
        return NotificationResponse(**notification.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании уведомления: {str(e)}"
        )


@router.post("/notifications/from-template", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification_from_template(
    request: CreateNotificationFromTemplateRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание уведомления из шаблона."""
    notification_service = NotificationService(db)
    
    try:
        notification = await notification_service.create_notification_from_template(
            user_id=user_id,
            template_name=request.template_name,
            variables=request.variables,
            recipient_email=request.recipient_email,
            recipient_phone=request.recipient_phone,
            recipient_device_token=request.recipient_device_token,
            priority=request.priority,
            scheduled_at=request.scheduled_at
        )
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Шаблон не найден или неактивен"
            )
        
        return NotificationResponse(**notification.to_dict())
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании уведомления из шаблона: {str(e)}"
        )


@router.get("/notifications", response_model=List[NotificationResponse])
async def get_my_notifications(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    notification_type: Optional[NotificationType] = Query(None, description="Тип уведомления для фильтрации"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение уведомлений пользователя."""
    notification_service = NotificationService(db)
    
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=user_id,
            notification_type=notification_type,
            skip=skip,
            limit=limit
        )
        
        return [NotificationResponse(**notification.to_dict()) for notification in notifications]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении уведомлений: {str(e)}"
        )


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение уведомления по ID."""
    notification_service = NotificationService(db)
    
    notification = await notification_service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    # Проверяем, что уведомление принадлежит пользователю
    if notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    return NotificationResponse(**notification.to_dict())


@router.post("/notifications/{notification_id}/send", status_code=status.HTTP_200_OK)
async def send_notification(
    notification_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Отправка уведомления."""
    notification_service = NotificationService(db)
    
    # Проверяем, что уведомление принадлежит пользователю
    notification = await notification_service.get_notification_by_id(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уведомление не найдено"
        )
    
    if notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        success = await notification_service.send_notification(notification_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при отправке уведомления"
            )
        
        return {"message": "Уведомление успешно отправлено"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отправке уведомления: {str(e)}"
        )


@router.get("/notifications/me/stats", response_model=NotificationStatsResponse)
async def get_my_notification_stats(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики уведомлений пользователя."""
    notification_service = NotificationService(db)
    
    try:
        stats = await notification_service.get_notification_stats(user_id)
        return NotificationStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики уведомлений: {str(e)}"
        )
