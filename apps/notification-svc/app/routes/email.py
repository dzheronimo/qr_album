"""
Маршруты для работы с email уведомлениями.

Содержит эндпоинты для отправки email уведомлений.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import Settings

router = APIRouter()
settings = Settings()


class EmailRequest(BaseModel):
    """Модель запроса для отправки email."""
    to: str
    subject: str
    text: str


class EmailResponse(BaseModel):
    """Модель ответа при отправке email."""
    success: bool
    message: str


@router.post("/notify/email", response_model=EmailResponse)
async def send_email(request: EmailRequest) -> EmailResponse:
    """
    Отправка email уведомления.
    
    Args:
        request: Данные для отправки email
        
    Returns:
        EmailResponse: Результат отправки email
        
    Raises:
        HTTPException: При ошибке отправки email
    """
    try:
        # Создание сообщения
        message = MIMEMultipart()
        message["From"] = settings.smtp_from_email
        message["To"] = request.to
        message["Subject"] = request.subject
        
        # Добавление текста сообщения
        message.attach(MIMEText(request.text, "plain"))
        
        # Отправка email
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            use_tls=settings.smtp_use_tls,
            username=settings.smtp_user,
            password=settings.smtp_password,
        )
        
        return EmailResponse(
            success=True,
            message="Email sent successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )
