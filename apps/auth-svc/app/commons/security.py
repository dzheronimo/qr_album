"""
Модуль для работы с JWT токенами и безопасностью.

Содержит функции для создания и декодирования JWT токенов,
а также другие утилиты безопасности.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from loguru import logger


def create_access_token(
    subject: str,
    secret: str,
    minutes: int = 15,
    algorithm: str = "HS256",
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Создает JWT токен доступа.

    Args:
        subject: Идентификатор субъекта (обычно user_id)
        secret: Секретный ключ для подписи токена
        minutes: Время жизни токена в минутах
        algorithm: Алгоритм подписи токена
        additional_claims: Дополнительные claims для токена

    Returns:
        JWT токен в виде строки

    Raises:
        ValueError: Если subject пустой или secret не задан
    """
    if not subject:
        raise ValueError("Subject cannot be empty")
    if not secret:
        raise ValueError("Secret cannot be empty")

    expire = datetime.utcnow() + timedelta(minutes=minutes)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    if additional_claims:
        to_encode.update(additional_claims)

    try:
        encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
        logger.debug(f"Created access token for subject: {subject}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise


def decode_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> Dict[str, Any]:
    """
    Декодирует и проверяет JWT токен.

    Args:
        token: JWT токен для декодирования
        secret: Секретный ключ для проверки подписи
        algorithm: Алгоритм подписи токена

    Returns:
        Словарь с claims из токена

    Raises:
        JWTError: Если токен невалидный или истек
        ValueError: Если токен или secret пустые
    """
    if not token:
        raise ValueError("Token cannot be empty")
    if not secret:
        raise ValueError("Secret cannot be empty")

    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        logger.debug(f"Successfully decoded token for subject: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.warning(f"Failed to decode token: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while decoding token: {e}")
        raise


def verify_token_expiry(payload: Dict[str, Any]) -> bool:
    """
    Проверяет, не истек ли токен.

    Args:
        payload: Декодированный payload токена

    Returns:
        True если токен не истек, False если истек
    """
    exp = payload.get("exp")
    if not exp:
        return False
    
    try:
        exp_datetime = datetime.fromtimestamp(exp)
        return exp_datetime > datetime.utcnow()
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid exp claim in token: {e}")
        return False


def create_refresh_token(
    subject: str,
    secret: str,
    minutes: int = 7 * 24 * 60,  # 7 дней по умолчанию
    algorithm: str = "HS256",
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Создает JWT refresh токен.

    Args:
        subject: Идентификатор субъекта (обычно user_id)
        secret: Секретный ключ для подписи токена
        minutes: Время жизни токена в минутах
        algorithm: Алгоритм подписи токена
        additional_claims: Дополнительные claims для токена

    Returns:
        JWT refresh токен в виде строки

    Raises:
        ValueError: Если subject пустой или secret не задан
    """
    if not subject:
        raise ValueError("Subject cannot be empty")
    if not secret:
        raise ValueError("Secret cannot be empty")

    expire = datetime.utcnow() + timedelta(minutes=minutes)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",  # Указываем тип токена
    }
    
    if additional_claims:
        to_encode.update(additional_claims)

    try:
        encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
        logger.debug(f"Created refresh token for subject: {subject}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create refresh token: {e}")
        raise


def extract_user_id_from_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> Optional[str]:
    """
    Извлекает user_id из JWT токена.

    Args:
        token: JWT токен
        secret: Секретный ключ
        algorithm: Алгоритм подписи

    Returns:
        user_id из токена или None если не удалось извлечь
    """
    try:
        payload = decode_token(token, secret, algorithm)
        if verify_token_expiry(payload):
            return payload.get("sub")
        return None
    except Exception as e:
        logger.warning(f"Failed to extract user_id from token: {e}")
        return None