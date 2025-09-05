"""
Сервис для работы с медиафайлами.

Содержит бизнес-логику для CRUD операций с медиафайлами.
"""

import mimetypes
import os
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError
import boto3
from botocore.exceptions import ClientError

from app.models.media_file import MediaFile, MediaType, MediaStatus
from app.config import Settings

settings = Settings()


class MediaService:
    """Сервис для работы с медиафайлами."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name='us-east-1'
        )
    
    def _get_file_type(self, mime_type: str) -> MediaType:
        """
        Определение типа файла по MIME типу.
        
        Args:
            mime_type: MIME тип файла
            
        Returns:
            MediaType: Тип медиафайла
        """
        if mime_type.startswith('image/'):
            return MediaType.IMAGE
        elif mime_type.startswith('video/'):
            return MediaType.VIDEO
        elif mime_type.startswith('audio/'):
            return MediaType.AUDIO
        elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return MediaType.DOCUMENT
        else:
            return MediaType.OTHER
    
    async def create_media_file(
        self,
        user_id: int,
        filename: str,
        original_filename: str,
        mime_type: str,
        file_size: int,
        s3_key: str,
        page_id: Optional[int] = None,
        album_id: Optional[int] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None
    ) -> MediaFile:
        """
        Создание записи о медиафайле.
        
        Args:
            user_id: ID пользователя
            filename: Имя файла
            original_filename: Оригинальное имя файла
            mime_type: MIME тип файла
            file_size: Размер файла в байтах
            s3_key: Ключ в S3/MinIO
            page_id: ID страницы (опционально)
            album_id: ID альбома (опционально)
            description: Описание файла
            tags: Теги файла (JSON строка)
            
        Returns:
            MediaFile: Созданный медиафайл
        """
        file_type = self._get_file_type(mime_type)
        
        media_file = MediaFile(
            user_id=user_id,
            filename=filename,
            original_filename=original_filename,
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            s3_key=s3_key,
            s3_bucket=settings.minio_bucket_name,
            page_id=page_id,
            album_id=album_id,
            description=description,
            tags=tags,
            status=MediaStatus.UPLOADING
        )
        
        try:
            self.db.add(media_file)
            await self.db.commit()
            await self.db.refresh(media_file)
            return media_file
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании записи о медиафайле")
    
    async def get_media_file_by_id(self, media_id: int, user_id: Optional[int] = None) -> Optional[MediaFile]:
        """
        Получение медиафайла по ID.
        
        Args:
            media_id: ID медиафайла
            user_id: ID пользователя (для проверки доступа)
            
        Returns:
            Optional[MediaFile]: Медиафайл или None
        """
        query = select(MediaFile).where(MediaFile.id == media_id)
        
        if user_id is not None:
            query = query.where(MediaFile.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_media_files_by_page(
        self,
        page_id: int,
        user_id: Optional[int] = None,
        status: Optional[MediaStatus] = None
    ) -> List[MediaFile]:
        """
        Получение медиафайлов страницы.
        
        Args:
            page_id: ID страницы
            user_id: ID пользователя (для проверки доступа)
            status: Фильтр по статусу
            
        Returns:
            List[MediaFile]: Список медиафайлов
        """
        query = select(MediaFile).where(MediaFile.page_id == page_id)
        
        if user_id is not None:
            query = query.where(MediaFile.user_id == user_id)
        
        if status is not None:
            query = query.where(MediaFile.status == status)
        
        query = query.order_by(MediaFile.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_media_files_by_album(
        self,
        album_id: int,
        user_id: Optional[int] = None,
        status: Optional[MediaStatus] = None
    ) -> List[MediaFile]:
        """
        Получение медиафайлов альбома.
        
        Args:
            album_id: ID альбома
            user_id: ID пользователя (для проверки доступа)
            status: Фильтр по статусу
            
        Returns:
            List[MediaFile]: Список медиафайлов
        """
        query = select(MediaFile).where(MediaFile.album_id == album_id)
        
        if user_id is not None:
            query = query.where(MediaFile.user_id == user_id)
        
        if status is not None:
            query = query.where(MediaFile.status == status)
        
        query = query.order_by(MediaFile.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_media_files(
        self,
        user_id: int,
        file_type: Optional[MediaType] = None,
        status: Optional[MediaStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MediaFile]:
        """
        Получение медиафайлов пользователя.
        
        Args:
            user_id: ID пользователя
            file_type: Фильтр по типу файла
            status: Фильтр по статусу
            limit: Лимит записей
            offset: Смещение
            
        Returns:
            List[MediaFile]: Список медиафайлов
        """
        query = select(MediaFile).where(MediaFile.user_id == user_id)
        
        if file_type is not None:
            query = query.where(MediaFile.file_type == file_type)
        
        if status is not None:
            query = query.where(MediaFile.status == status)
        
        query = query.order_by(MediaFile.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_media_file(
        self,
        media_id: int,
        user_id: int,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[float] = None
    ) -> Optional[MediaFile]:
        """
        Обновление медиафайла.
        
        Args:
            media_id: ID медиафайла
            user_id: ID пользователя
            description: Новое описание
            tags: Новые теги
            width: Ширина (для изображений/видео)
            height: Высота (для изображений/видео)
            duration: Длительность (для видео/аудио)
            
        Returns:
            Optional[MediaFile]: Обновленный медиафайл или None
        """
        media_file = await self.get_media_file_by_id(media_id, user_id)
        if not media_file:
            return None
        
        update_data = {}
        
        if description is not None:
            update_data["description"] = description
        if tags is not None:
            update_data["tags"] = tags
        if width is not None:
            update_data["width"] = width
        if height is not None:
            update_data["height"] = height
        if duration is not None:
            update_data["duration"] = duration
        
        if not update_data:
            return media_file
        
        update_data["updated_at"] = datetime.utcnow()
        
        await self.db.execute(
            update(MediaFile)
            .where(MediaFile.id == media_id)
            .where(MediaFile.user_id == user_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return await self.get_media_file_by_id(media_id, user_id)
    
    async def mark_as_ready(self, media_id: int, s3_url: Optional[str] = None) -> bool:
        """
        Отметка медиафайла как готового.
        
        Args:
            media_id: ID медиафайла
            s3_url: URL файла в S3/MinIO
            
        Returns:
            bool: True если обновление успешно, False иначе
        """
        update_data = {
            "status": MediaStatus.READY,
            "updated_at": datetime.utcnow()
        }
        
        if s3_url is not None:
            update_data["s3_url"] = s3_url
        
        await self.db.execute(
            update(MediaFile)
            .where(MediaFile.id == media_id)
            .values(**update_data)
        )
        await self.db.commit()
        
        return True
    
    async def mark_as_error(self, media_id: int, error_message: str) -> bool:
        """
        Отметка медиафайла как ошибочного.
        
        Args:
            media_id: ID медиафайла
            error_message: Сообщение об ошибке
            
        Returns:
            bool: True если обновление успешно, False иначе
        """
        await self.db.execute(
            update(MediaFile)
            .where(MediaFile.id == media_id)
            .values(
                status=MediaStatus.ERROR,
                processing_error=error_message,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def delete_media_file(self, media_id: int, user_id: int) -> bool:
        """
        Удаление медиафайла.
        
        Args:
            media_id: ID медиафайла
            user_id: ID пользователя
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        media_file = await self.get_media_file_by_id(media_id, user_id)
        if not media_file:
            return False
        
        # Удаление файла из S3/MinIO
        try:
            self.s3_client.delete_object(
                Bucket=media_file.s3_bucket,
                Key=media_file.s3_key
            )
        except ClientError as e:
            # Логируем ошибку, но продолжаем удаление записи
            print(f"Failed to delete file from S3: {e}")
        
        # Удаление записи из базы данных
        await self.db.execute(
            delete(MediaFile)
            .where(MediaFile.id == media_id)
            .where(MediaFile.user_id == user_id)
        )
        await self.db.commit()
        
        return True
    
    async def get_media_stats(self, user_id: int) -> dict:
        """
        Получение статистики медиафайлов пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            dict: Статистика медиафайлов
        """
        # Общее количество файлов
        total_query = select(func.count(MediaFile.id)).where(MediaFile.user_id == user_id)
        total_result = await self.db.execute(total_query)
        total_files = total_result.scalar() or 0
        
        # Количество по типам
        type_query = select(MediaFile.file_type, func.count(MediaFile.id)).where(
            MediaFile.user_id == user_id
        ).group_by(MediaFile.file_type)
        type_result = await self.db.execute(type_query)
        files_by_type = {row[0].value: row[1] for row in type_result}
        
        # Общий размер файлов
        size_query = select(func.sum(MediaFile.file_size)).where(MediaFile.user_id == user_id)
        size_result = await self.db.execute(size_query)
        total_size = size_result.scalar() or 0
        
        return {
            "total_files": total_files,
            "files_by_type": files_by_type,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024) if total_size > 0 else 0,
        }
    
    def generate_presigned_upload(
        self,
        s3_key: str,
        content_type: str,
        expires_in: int = 600
    ) -> dict:
        """
        Генерация presigned POST для загрузки файла.
        
        Args:
            s3_key: Ключ файла в S3/MinIO
            content_type: MIME тип файла
            expires_in: Время жизни в секундах
            
        Returns:
            dict: Presigned POST данные
        """
        try:
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=settings.minio_bucket_name,
                Key=s3_key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 1, 100 * 1024 * 1024]  # Максимум 100MB
                ],
                ExpiresIn=expires_in
            )
            return presigned_post
        except ClientError as e:
            raise ValueError(f"Failed to create presigned POST: {str(e)}")
    
    def generate_presigned_download(self, s3_key: str, expires_in: int = 3600) -> str:
        """
        Генерация presigned URL для скачивания файла.
        
        Args:
            s3_key: Ключ файла в S3/MinIO
            expires_in: Время жизни в секундах
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.minio_bucket_name, 'Key': s3_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise ValueError(f"Failed to create presigned URL: {str(e)}")
