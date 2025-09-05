"""
Модели для QR кодов.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class QRCodeStatus(str, Enum):
    """Статусы QR кода."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class QRCodeType(str, Enum):
    """Типы QR кода."""
    PAGE = "page"  # Ссылка на страницу альбома
    ALBUM = "album"  # Ссылка на альбом
    CUSTOM = "custom"  # Кастомная ссылка


class QRCode(Base):
    """Модель QR кода."""
    
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Основная информация
    name = Column(String(255), nullable=False, comment="Название QR кода")
    description = Column(Text, nullable=True, comment="Описание QR кода")
    
    # Тип и статус
    qr_type = Column(String(50), nullable=False, default=QRCodeType.PAGE, comment="Тип QR кода")
    status = Column(String(50), nullable=False, default=QRCodeStatus.ACTIVE, comment="Статус QR кода")
    
    # Связи с контентом (без внешних ключей, так как таблицы в других сервисах)
    page_id = Column(Integer, nullable=True, comment="ID страницы (если тип PAGE)")
    album_id = Column(Integer, nullable=True, comment="ID альбома (если тип ALBUM)")
    custom_url = Column(String(500), nullable=True, comment="Кастомная ссылка (если тип CUSTOM)")
    
    # Владелец
    user_id = Column(Integer, nullable=False, comment="ID пользователя-владельца")
    
    # Настройки QR кода
    qr_data = Column(Text, nullable=False, comment="Данные для генерации QR кода")
    qr_image_url = Column(String(500), nullable=True, comment="URL изображения QR кода")
    
    # Кастомизация
    foreground_color = Column(String(7), nullable=True, default="#000000", comment="Цвет переднего плана (hex)")
    background_color = Column(String(7), nullable=True, default="#FFFFFF", comment="Цвет фона (hex)")
    logo_url = Column(String(500), nullable=True, comment="URL логотипа для QR кода")
    size = Column(Integer, nullable=True, default=200, comment="Размер QR кода в пикселях")
    
    # Статистика
    scan_count = Column(Integer, nullable=False, default=0, comment="Количество сканирований")
    last_scan_at = Column(DateTime, nullable=True, comment="Время последнего сканирования")
    
    # Метаданные
    extra_data = Column(JSON, nullable=True, comment="Дополнительные метаданные")
    
    # Временные метки
    created_at = Column(DateTime, nullable=False, default=func.now(), comment="Время создания")
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now(), comment="Время обновления")
    expires_at = Column(DateTime, nullable=True, comment="Время истечения (если применимо)")
    
    def to_dict(self) -> dict:
        """Преобразование в словарь."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "qr_type": self.qr_type,
            "status": self.status,
            "page_id": self.page_id,
            "album_id": self.album_id,
            "custom_url": self.custom_url,
            "user_id": self.user_id,
            "qr_data": self.qr_data,
            "qr_image_url": self.qr_image_url,
            "foreground_color": self.foreground_color,
            "background_color": self.background_color,
            "logo_url": self.logo_url,
            "size": self.size,
            "scan_count": self.scan_count,
            "last_scan_at": self.last_scan_at.isoformat() if self.last_scan_at else None,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class QRCodeScan(Base):
    """Модель для отслеживания сканирований QR кодов."""
    
    __tablename__ = "qr_code_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Связь с QR кодом
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False, comment="ID QR кода")
    
    # Информация о сканировании
    ip_address = Column(String(45), nullable=True, comment="IP адрес сканера")
    user_agent = Column(Text, nullable=True, comment="User Agent браузера")
    referer = Column(String(500), nullable=True, comment="Referer страницы")
    
    # Геолокация (если доступна)
    country = Column(String(100), nullable=True, comment="Страна")
    city = Column(String(100), nullable=True, comment="Город")
    latitude = Column(String(20), nullable=True, comment="Широта")
    longitude = Column(String(20), nullable=True, comment="Долгота")
    
    # Дополнительная информация
    device_type = Column(String(50), nullable=True, comment="Тип устройства (mobile, desktop, tablet)")
    browser = Column(String(100), nullable=True, comment="Браузер")
    os = Column(String(100), nullable=True, comment="Операционная система")
    
    # Временная метка
    scanned_at = Column(DateTime, nullable=False, default=func.now(), comment="Время сканирования")
    
    # Связь с QR кодом
    qr_code = relationship("QRCode", backref="scans")
    
    def to_dict(self) -> dict:
        """Преобразование в словарь."""
        return {
            "id": self.id,
            "qr_code_id": self.qr_code_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "referer": self.referer,
            "country": self.country,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "device_type": self.device_type,
            "browser": self.browser,
            "os": self.os,
            "scanned_at": self.scanned_at.isoformat(),
        }
