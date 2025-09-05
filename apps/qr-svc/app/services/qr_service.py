"""
Сервис для работы с QR кодами.
"""

import qrcode
import qrcode.image.svg
from io import BytesIO
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.qr_code import QRCode, QRCodeScan, QRCodeStatus, QRCodeType
from app.config import Settings


class QRService:
    """Сервис для работы с QR кодами."""
    
    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings
    
    async def create_qr_code(
        self,
        name: str,
        qr_type: QRCodeType,
        user_id: int,
        page_id: Optional[int] = None,
        album_id: Optional[int] = None,
        custom_url: Optional[str] = None,
        description: Optional[str] = None,
        foreground_color: str = "#000000",
        background_color: str = "#FFFFFF",
        logo_url: Optional[str] = None,
        size: int = 200,
        expires_at: Optional[datetime] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> QRCode:
        """Создание нового QR кода."""
        
        # Генерируем данные для QR кода
        qr_data = await self._generate_qr_data(qr_type, page_id, album_id, custom_url)
        
        # Создаем QR код
        qr_code = QRCode(
            name=name,
            description=description,
            qr_type=qr_type,
            status=QRCodeStatus.ACTIVE,
            page_id=page_id,
            album_id=album_id,
            custom_url=custom_url,
            user_id=user_id,
            qr_data=qr_data,
            foreground_color=foreground_color,
            background_color=background_color,
            logo_url=logo_url,
            size=size,
            expires_at=expires_at,
            extra_data=extra_data
        )
        
        self.db.add(qr_code)
        await self.db.commit()
        await self.db.refresh(qr_code)
        
        # Генерируем изображение QR кода
        qr_image_url = await self._generate_qr_image(qr_code)
        qr_code.qr_image_url = qr_image_url
        
        await self.db.commit()
        await self.db.refresh(qr_code)
        
        return qr_code
    
    async def get_qr_code(self, qr_code_id: int, user_id: int) -> Optional[QRCode]:
        """Получение QR кода по ID."""
        result = await self.db.execute(
            select(QRCode)
            .where(and_(QRCode.id == qr_code_id, QRCode.user_id == user_id))
        )
        return result.scalar_one_or_none()
    
    async def get_qr_codes(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        qr_type: Optional[QRCodeType] = None,
        status: Optional[QRCodeStatus] = None
    ) -> List[QRCode]:
        """Получение списка QR кодов пользователя."""
        query = select(QRCode).where(QRCode.user_id == user_id)
        
        if qr_type:
            query = query.where(QRCode.qr_type == qr_type)
        
        if status:
            query = query.where(QRCode.status == status)
        
        query = query.offset(skip).limit(limit).order_by(QRCode.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_qr_code(
        self,
        qr_code_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        foreground_color: Optional[str] = None,
        background_color: Optional[str] = None,
        logo_url: Optional[str] = None,
        size: Optional[int] = None,
        status: Optional[QRCodeStatus] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Optional[QRCode]:
        """Обновление QR кода."""
        qr_code = await self.get_qr_code(qr_code_id, user_id)
        if not qr_code:
            return None
        
        # Обновляем поля
        if name is not None:
            qr_code.name = name
        if description is not None:
            qr_code.description = description
        if foreground_color is not None:
            qr_code.foreground_color = foreground_color
        if background_color is not None:
            qr_code.background_color = background_color
        if logo_url is not None:
            qr_code.logo_url = logo_url
        if size is not None:
            qr_code.size = size
        if status is not None:
            qr_code.status = status
        if extra_data is not None:
            qr_code.extra_data = extra_data
        
        # Если изменились параметры внешнего вида, перегенерируем изображение
        if any([foreground_color, background_color, logo_url, size]):
            qr_image_url = await self._generate_qr_image(qr_code)
            qr_code.qr_image_url = qr_image_url
        
        await self.db.commit()
        await self.db.refresh(qr_code)
        
        return qr_code
    
    async def delete_qr_code(self, qr_code_id: int, user_id: int) -> bool:
        """Удаление QR кода."""
        qr_code = await self.get_qr_code(qr_code_id, user_id)
        if not qr_code:
            return False
        
        await self.db.delete(qr_code)
        await self.db.commit()
        
        return True
    
    async def get_qr_code_by_data(self, qr_data: str) -> Optional[QRCode]:
        """Получение QR кода по данным (для сканирования)."""
        result = await self.db.execute(
            select(QRCode)
            .where(and_(
                QRCode.qr_data == qr_data,
                QRCode.status == QRCodeStatus.ACTIVE,
                or_(
                    QRCode.expires_at.is_(None),
                    QRCode.expires_at > datetime.utcnow()
                )
            ))
        )
        return result.scalar_one_or_none()
    
    async def record_scan(
        self,
        qr_code_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referer: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        latitude: Optional[str] = None,
        longitude: Optional[str] = None,
        device_type: Optional[str] = None,
        browser: Optional[str] = None,
        os: Optional[str] = None
    ) -> QRCodeScan:
        """Запись сканирования QR кода."""
        
        # Создаем запись о сканировании
        scan = QRCodeScan(
            qr_code_id=qr_code_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            country=country,
            city=city,
            latitude=latitude,
            longitude=longitude,
            device_type=device_type,
            browser=browser,
            os=os
        )
        
        self.db.add(scan)
        
        # Обновляем статистику QR кода
        qr_code = await self.db.get(QRCode, qr_code_id)
        if qr_code:
            qr_code.scan_count += 1
            qr_code.last_scan_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(scan)
        
        return scan
    
    async def get_qr_code_stats(self, qr_code_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение статистики QR кода."""
        qr_code = await self.get_qr_code(qr_code_id, user_id)
        if not qr_code:
            return None
        
        # Получаем общую статистику сканирований
        total_scans = qr_code.scan_count
        
        # Получаем статистику по дням за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_stats = await self.db.execute(
            select(
                func.date(QRCodeScan.scanned_at).label('date'),
                func.count(QRCodeScan.id).label('count')
            )
            .where(and_(
                QRCodeScan.qr_code_id == qr_code_id,
                QRCodeScan.scanned_at >= thirty_days_ago
            ))
            .group_by(func.date(QRCodeScan.scanned_at))
            .order_by(func.date(QRCodeScan.scanned_at))
        )
        
        # Получаем статистику по странам
        country_stats = await self.db.execute(
            select(
                QRCodeScan.country,
                func.count(QRCodeScan.id).label('count')
            )
            .where(QRCodeScan.qr_code_id == qr_code_id)
            .group_by(QRCodeScan.country)
            .order_by(func.count(QRCodeScan.id).desc())
            .limit(10)
        )
        
        # Получаем статистику по устройствам
        device_stats = await self.db.execute(
            select(
                QRCodeScan.device_type,
                func.count(QRCodeScan.id).label('count')
            )
            .where(QRCodeScan.qr_code_id == qr_code_id)
            .group_by(QRCodeScan.device_type)
            .order_by(func.count(QRCodeScan.id).desc())
        )
        
        return {
            "qr_code_id": qr_code_id,
            "total_scans": total_scans,
            "last_scan_at": qr_code.last_scan_at.isoformat() if qr_code.last_scan_at else None,
            "daily_stats": [{"date": str(row.date), "count": row.count} for row in daily_stats],
            "country_stats": [{"country": row.country, "count": row.count} for row in country_stats],
            "device_stats": [{"device_type": row.device_type, "count": row.count} for row in device_stats],
        }
    
    async def _generate_qr_data(
        self,
        qr_type: QRCodeType,
        page_id: Optional[int] = None,
        album_id: Optional[int] = None,
        custom_url: Optional[str] = None
    ) -> str:
        """Генерация данных для QR кода."""
        base_url = self.settings.scan_gateway_url or "http://localhost:8004"
        
        if qr_type == QRCodeType.PAGE and page_id:
            return f"{base_url}/scan/page/{page_id}"
        elif qr_type == QRCodeType.ALBUM and album_id:
            return f"{base_url}/scan/album/{album_id}"
        elif qr_type == QRCodeType.CUSTOM and custom_url:
            return custom_url
        else:
            raise ValueError(f"Invalid QR code type and parameters: {qr_type}")
    
    async def _generate_qr_image(self, qr_code: QRCode) -> str:
        """Генерация изображения QR кода."""
        # Создаем QR код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_code.qr_data)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(
            fill_color=qr_code.foreground_color,
            back_color=qr_code.background_color
        )
        
        # Изменяем размер если нужно
        if qr_code.size and qr_code.size != 200:
            img = img.resize((qr_code.size, qr_code.size))
        
        # TODO: Сохранение в MinIO или файловую систему
        # Пока возвращаем placeholder URL
        return f"/qr-images/{qr_code.id}.png"
