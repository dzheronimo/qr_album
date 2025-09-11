from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

security = HTTPBearer()

async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    Извлекает user_id из JWT токена.
    
    Args:
        credentials: JWT токен из заголовка Authorization
        
    Returns:
        int: ID пользователя
        
    Raises:
        HTTPException: При недействительном токене
    """
    try:
        # Получаем секретный ключ из переменных окружения
        secret_key = os.getenv('JWT_SECRET', 'your-secret-key')
        
        # Декодируем JWT токен
        payload = jwt.decode(credentials.credentials, secret_key, algorithms=['HS256'])
        
        # Извлекаем user_id из payload
        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Недействительный токен: отсутствует user_id'
            )
        
        return int(user_id)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Токен истек'
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Недействительный токен'
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Ошибка проверки токена: {str(e)}'
        )
