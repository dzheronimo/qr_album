"""
Роуты для аутентификации через API Gateway.
"""

import httpx
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger

from app.config import Settings

settings = Settings()
router = APIRouter()


class LoginRequest(BaseModel):
    """Запрос на вход."""
    email: str = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")


class RegisterRequest(BaseModel):
    """Запрос на регистрацию."""
    email: str = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена."""
    refresh_token: str = Field(..., description="Refresh токен")


@router.post("/auth/login")
async def login(request: LoginRequest):
    """
    Вход пользователя в систему.
    
    Args:
        request: Данные для входа
        
    Returns:
        Dict[str, Any]: Токены и информация о пользователе
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.auth_service_url}/auth/login",
                json=request.dict()
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"User logged in: {request.email}")
                return {"success": True, "data": data}
            else:
                # Handle non-200 responses - return the error response directly
                try:
                    error_data = response.json() if response.content else {"detail": "Ошибка входа"}
                    detail = error_data.get("detail", "Ошибка входа")
                except Exception:
                    detail = "Ошибка входа"
                
                logger.error(f"Login failed for user {request.email}: {response.status_code} - {detail}")
                # Return the error response in the expected format
                return {"success": False, "data": None, "error": detail}
                
    except httpx.TimeoutException:
        logger.error(f"Timeout when logging in user: {request.email}")
        return {"success": False, "data": None, "error": "Таймаут при входе в систему"}
    except httpx.ConnectError:
        logger.error(f"Connection error when logging in user: {request.email}")
        return {"success": False, "data": None, "error": "Сервис аутентификации недоступен"}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error when logging in user: {e.response.status_code}: {e.response.text}")
        return {"success": False, "data": None, "error": "Ошибка при входе в систему"}
    except Exception as e:
        logger.error(f"Error when logging in user: {str(e)}")
        return {"success": False, "data": None, "error": "Ошибка при входе в систему"}


@router.post("/auth/register")
async def register(request: RegisterRequest):
    """
    Регистрация нового пользователя.
    
    Args:
        request: Данные для регистрации
        
    Returns:
        Dict[str, Any]: Информация о созданном пользователе
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.auth_service_url}/auth/register",
                json=request.dict()
            )
            
            if response.status_code == 201:
                data = response.json()
                logger.info(f"User registered: {request.email}")
                return data
            else:
                error_data = response.json() if response.content else {"detail": "Ошибка регистрации"}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail", "Ошибка регистрации")
                )
                
    except httpx.TimeoutException:
        logger.error(f"Timeout when registering user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Таймаут при регистрации"
        )
    except httpx.ConnectError:
        logger.error(f"Connection error when registering user: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис аутентификации недоступен"
        )
    except Exception as e:
        logger.error(f"Error when registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации"
        )


@router.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """
    Обновление токена доступа.
    
    Args:
        request: Refresh токен
        
    Returns:
        Dict[str, Any]: Новые токены
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.auth_service_url}/auth/refresh",
                json=request.dict()
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Token refreshed successfully")
                return data
            else:
                error_data = response.json() if response.content else {"detail": "Ошибка обновления токена"}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail", "Ошибка обновления токена")
                )
                
    except httpx.TimeoutException:
        logger.error("Timeout when refreshing token")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Таймаут при обновлении токена"
        )
    except httpx.ConnectError:
        logger.error("Connection error when refreshing token")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис аутентификации недоступен"
        )
    except Exception as e:
        logger.error(f"Error when refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении токена"
        )


@router.get("/auth/me")
async def get_current_user(request: Request):
    """
    Получение информации о текущем пользователе.
    
    Args:
        request: HTTP запрос (должен содержать токен)
        
    Returns:
        Dict[str, Any]: Информация о пользователе
    """
    # Проверяем, что пользователь аутентифицирован
    if not hasattr(request.state, 'is_authenticated') or not request.state.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не аутентифицирован"
        )
    
    try:
        # Получаем токен из заголовка
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не предоставлен"
            )
        
        token = auth_header.split(" ")[1]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.auth_service_url}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"User info retrieved: {request.state.user_id}")
                return data
            else:
                error_data = response.json() if response.content else {"detail": "Ошибка получения информации о пользователе"}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail", "Ошибка получения информации о пользователе")
                )
                
    except httpx.TimeoutException:
        logger.error(f"Timeout when getting user info: {request.state.user_id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Таймаут при получении информации о пользователе"
        )
    except httpx.ConnectError:
        logger.error(f"Connection error when getting user info: {request.state.user_id}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис аутентификации недоступен"
        )
    except Exception as e:
        logger.error(f"Error when getting user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении информации о пользователе"
        )


@router.post("/auth/logout")
async def logout(request: Request):
    """
    Выход пользователя из системы.
    
    Args:
        request: HTTP запрос (должен содержать токен)
        
    Returns:
        Dict[str, str]: Сообщение об успешном выходе
    """
    # Проверяем, что пользователь аутентифицирован
    if not hasattr(request.state, 'is_authenticated') or not request.state.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не аутентифицирован"
        )
    
    try:
        # Получаем токен из заголовка
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не предоставлен"
            )
        
        token = auth_header.split(" ")[1]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.auth_service_url}/auth/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                logger.info(f"User logged out: {request.state.user_id}")
                return {"message": "Успешный выход из системы"}
            else:
                error_data = response.json() if response.content else {"detail": "Ошибка выхода"}
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("detail", "Ошибка выхода")
                )
                
    except httpx.TimeoutException:
        logger.error(f"Timeout when logging out user: {request.state.user_id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Таймаут при выходе из системы"
        )
    except httpx.ConnectError:
        logger.error(f"Connection error when logging out user: {request.state.user_id}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис аутентификации недоступен"
        )
    except Exception as e:
        logger.error(f"Error when logging out user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выходе из системы"
        )
