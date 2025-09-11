"""
Маршруты для аутентификации.

Содержит эндпоинты для регистрации, входа, восстановления пароля и управления профилем.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.utils.password import validate_password_strength

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Модель запроса для входа."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Модель запроса для регистрации."""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class PasswordResetRequest(BaseModel):
    """Модель запроса для восстановления пароля."""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Модель запроса для подтверждения сброса пароля."""
    reset_token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    """Модель запроса для изменения пароля."""
    old_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    """Модель запроса для обновления профиля."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@router.post("/register")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя.
    
    Args:
        request: Данные для регистрации
        db: Сессия базы данных
        
    Returns:
        dict: Результат регистрации
        
    Raises:
        HTTPException: При ошибке регистрации
    """
    # Валидация пароля
    is_valid, errors = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"password_errors": errors}
        )
    
    auth_service = AuthService(db)
    
    try:
        result = await auth_service.register(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход пользователя в систему.
    
    Args:
        request: Данные для входа
        db: Сессия базы данных
        
    Returns:
        dict: Токены аутентификации
        
    Raises:
        HTTPException: При ошибке аутентификации
    """
    auth_service = AuthService(db)
    
    result = await auth_service.login(request.email, request.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    return result


@router.post("/verify-email/{verification_token}")
async def verify_email(
    verification_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Верификация email пользователя.
    
    Args:
        verification_token: Токен верификации
        db: Сессия базы данных
        
    Returns:
        dict: Результат верификации
        
    Raises:
        HTTPException: При ошибке верификации
    """
    auth_service = AuthService(db)
    
    success = await auth_service.verify_email(verification_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или истекший токен верификации"
        )
    
    return {"message": "Email успешно верифицирован"}


@router.post("/password-reset")
async def initiate_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Инициация восстановления пароля.
    
    Args:
        request: Email для восстановления пароля
        db: Сессия базы данных
        
    Returns:
        dict: Результат инициации восстановления
    """
    auth_service = AuthService(db)
    
    success = await auth_service.initiate_password_reset(request.email)
    
    # Всегда возвращаем успех для безопасности
    return {"message": "Если пользователь с таким email существует, инструкции отправлены на почту"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Подтверждение сброса пароля.
    
    Args:
        request: Данные для сброса пароля
        db: Сессия базы данных
        
    Returns:
        dict: Результат сброса пароля
        
    Raises:
        HTTPException: При ошибке сброса пароля
    """
    # Валидация нового пароля
    is_valid, errors = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"password_errors": errors}
        )
    
    auth_service = AuthService(db)
    
    success = await auth_service.reset_password(request.reset_token, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или истекший токен восстановления"
        )
    
    return {"message": "Пароль успешно изменен"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Изменение пароля пользователя.
    
    Args:
        request: Данные для изменения пароля
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Результат изменения пароля
        
    Raises:
        HTTPException: При ошибке изменения пароля
    """
    # Валидация нового пароля
    is_valid, errors = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"password_errors": errors}
        )
    
    auth_service = AuthService(db)
    
    success = await auth_service.change_password(
        user_id=user_id,
        old_password=request.old_password,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный старый пароль"
        )
    
    return {"message": "Пароль успешно изменен"}


@router.get("/me")
async def get_current_user(
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Получение текущего пользователя.
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Данные пользователя
        
    Raises:
        HTTPException: Если пользователь не найден
    """
    auth_service = AuthService(db)
    
    user_data = await auth_service.get_current_user(user_id)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user_data


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest,
    user_id: int,  # TODO: Получать из JWT токена
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление профиля пользователя.
    
    Args:
        request: Данные для обновления профиля
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        dict: Обновленные данные пользователя
        
    Raises:
        HTTPException: Если пользователь не найден
    """
    auth_service = AuthService(db)
    
    user_data = await auth_service.update_profile(
        user_id=user_id,
        first_name=request.first_name,
        last_name=request.last_name
    )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user_data


@router.get("/verify")
async def verify_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Проверяет JWT токен и возвращает информацию о пользователе.
    
    Args:
        request: HTTP запрос
        db: Сессия базы данных
        
    Returns:
        Dict[str, Any]: Информация о пользователе
        
    Raises:
        HTTPException: При недействительном токене
    """
    # Получаем токен из заголовка Authorization
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен аутентификации не предоставлен"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # Создаем сервис аутентификации
        auth_service = AuthService(db)
        
        # Проверяем токен
        user_info = await auth_service.verify_token(token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен аутентификации"
            )
        
        return user_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка проверки токена"
        )
