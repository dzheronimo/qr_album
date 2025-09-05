"""
Роуты для работы с платежами.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.payment_service import PaymentService
from app.models.billing import PaymentStatus, PaymentMethod

router = APIRouter()


class CreatePaymentRequest(BaseModel):
    """Запрос на создание платежа."""
    amount: Decimal = Field(..., gt=0, description="Сумма платежа")
    currency: str = Field(default="USD", min_length=3, max_length=3, description="Валюта")
    payment_method: PaymentMethod = Field(..., description="Метод платежа")
    subscription_id: Optional[int] = Field(None, description="ID подписки")
    description: Optional[str] = Field(None, description="Описание платежа")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="Дополнительные данные")


class ProcessPaymentRequest(BaseModel):
    """Запрос на обработку платежа."""
    external_transaction_id: Optional[str] = Field(None, description="Внешний ID транзакции")


class RefundPaymentRequest(BaseModel):
    """Запрос на возврат платежа."""
    amount: Optional[Decimal] = Field(None, gt=0, description="Сумма возврата")
    reason: Optional[str] = Field(None, description="Причина возврата")


class PaymentResponse(BaseModel):
    """Ответ с информацией о платеже."""
    id: int
    user_id: int
    subscription_id: Optional[int]
    amount: float
    currency: str
    payment_method: str
    status: str
    external_payment_id: Optional[str]
    external_transaction_id: Optional[str]
    description: Optional[str]
    payment_date: Optional[str]
    processed_at: Optional[str]
    extra_data: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class PaymentStatsResponse(BaseModel):
    """Ответ со статистикой платежей."""
    user_id: int
    total_payments: int
    successful_payments: int
    total_amount: float
    payments_by_status: Dict[str, int]
    payments_by_method: Dict[str, int]


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: CreatePaymentRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Создание платежа."""
    payment_service = PaymentService(db)
    
    try:
        payment = await payment_service.create_payment(
            user_id=user_id,
            amount=request.amount,
            currency=request.currency,
            payment_method=request.payment_method,
            subscription_id=request.subscription_id,
            description=request.description,
            extra_data=request.extra_data
        )
        
        return PaymentResponse(**payment.to_dict())
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании платежа: {str(e)}"
        )


@router.get("/payments", response_model=List[PaymentResponse])
async def get_my_payments(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    status: Optional[PaymentStatus] = Query(None, description="Статус платежа для фильтрации"),
    skip: int = Query(0, ge=0, description="Количество пропускаемых записей"),
    limit: int = Query(50, ge=1, le=100, description="Максимальное количество записей"),
    db: AsyncSession = Depends(get_db)
):
    """Получение платежей пользователя."""
    payment_service = PaymentService(db)
    
    try:
        payments = await payment_service.get_user_payments(
            user_id=user_id,
            status=status,
            skip=skip,
            limit=limit
        )
        
        return [PaymentResponse(**payment.to_dict()) for payment in payments]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении платежей: {str(e)}"
        )


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение платежа по ID."""
    payment_service = PaymentService(db)
    
    payment = await payment_service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )
    
    # Проверяем, что платеж принадлежит пользователю
    if payment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    return PaymentResponse(**payment.to_dict())


@router.post("/payments/{payment_id}/process", status_code=status.HTTP_200_OK)
async def process_payment(
    payment_id: int,
    request: ProcessPaymentRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Обработка платежа."""
    payment_service = PaymentService(db)
    
    # Проверяем, что платеж принадлежит пользователю
    payment = await payment_service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )
    
    if payment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        success = await payment_service.process_payment(
            payment_id=payment_id,
            external_transaction_id=request.external_transaction_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при обработке платежа"
            )
        
        return {"message": "Платеж успешно обработан"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обработке платежа: {str(e)}"
        )


@router.post("/payments/{payment_id}/refund", status_code=status.HTTP_200_OK)
async def refund_payment(
    payment_id: int,
    request: RefundPaymentRequest,
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Возврат платежа."""
    payment_service = PaymentService(db)
    
    # Проверяем, что платеж принадлежит пользователю
    payment = await payment_service.get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Платеж не найден"
        )
    
    if payment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещен"
        )
    
    try:
        success = await payment_service.refund_payment(
            payment_id=payment_id,
            amount=request.amount,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при возврате платежа"
            )
        
        return {"message": "Платеж успешно возвращен"}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при возврате платежа: {str(e)}"
        )


@router.get("/payments/me/stats", response_model=PaymentStatsResponse)
async def get_my_payment_stats(
    user_id: int = Query(..., description="ID пользователя"),  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики платежей пользователя."""
    payment_service = PaymentService(db)
    
    try:
        stats = await payment_service.get_payment_stats(user_id)
        return PaymentStatsResponse(**stats)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статистики платежей: {str(e)}"
        )
