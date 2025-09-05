"""
Сервис для работы с WeasyPrint.

Содержит интеграцию с WeasyPrint для генерации PDF и изображений.
"""

import os
import asyncio
import tempfile
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.print_models import PrintJob, PrintJobStatus, PrintFormat
from app.config import Settings

settings = Settings()


class WeasyPrintService:
    """Сервис для работы с WeasyPrint."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.output_dir = Path(settings.output_directory)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_pdf(
        self,
        job: PrintJob,
        html_content: str,
        css_content: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Генерация PDF из HTML.
        
        Args:
            job: Задание печати
            html_content: HTML контент
            css_content: CSS стили
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (успех, путь к файлу, сообщение об ошибке)
        """
        try:
            # В реальном приложении здесь была бы интеграция с WeasyPrint
            # Для демонстрации используем заглушку
            return await self._mock_pdf_generation(job, html_content, css_content)
            
        except Exception as e:
            return False, None, f"Ошибка генерации PDF: {str(e)}"
    
    async def generate_image(
        self,
        job: PrintJob,
        html_content: str,
        css_content: Optional[str] = None,
        format: PrintFormat = PrintFormat.PNG
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Генерация изображения из HTML.
        
        Args:
            job: Задание печати
            html_content: HTML контент
            css_content: CSS стили
            format: Формат изображения
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (успех, путь к файлу, сообщение об ошибке)
        """
        try:
            # В реальном приложении здесь была бы интеграция с WeasyPrint
            # Для демонстрации используем заглушку
            return await self._mock_image_generation(job, html_content, css_content, format)
            
        except Exception as e:
            return False, None, f"Ошибка генерации изображения: {str(e)}"
    
    async def _mock_pdf_generation(
        self,
        job: PrintJob,
        html_content: str,
        css_content: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Заглушка для генерации PDF.
        
        Args:
            job: Задание печати
            html_content: HTML контент
            css_content: CSS стили
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (успех, путь к файлу, сообщение об ошибке)
        """
        # Имитируем задержку обработки
        await asyncio.sleep(0.5)
        
        # Создаем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"print_job_{job.id}_{timestamp}.pdf"
        file_path = self.output_dir / filename
        
        # В реальном приложении здесь был бы вызов WeasyPrint
        # Создаем заглушку PDF файла
        try:
            # Создаем простой PDF заглушку
            pdf_content = self._create_mock_pdf(job, html_content)
            
            with open(file_path, 'wb') as f:
                f.write(pdf_content)
            
            return True, str(file_path), None
            
        except Exception as e:
            return False, None, f"Ошибка создания PDF файла: {str(e)}"
    
    async def _mock_image_generation(
        self,
        job: PrintJob,
        html_content: str,
        css_content: Optional[str] = None,
        format: PrintFormat = PrintFormat.PNG
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Заглушка для генерации изображения.
        
        Args:
            job: Задание печати
            html_content: HTML контент
            css_content: CSS стили
            format: Формат изображения
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (успех, путь к файлу, сообщение об ошибке)
        """
        # Имитируем задержку обработки
        await asyncio.sleep(0.3)
        
        # Создаем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"print_job_{job.id}_{timestamp}.{format.value}"
        file_path = self.output_dir / filename
        
        # В реальном приложении здесь был бы вызов WeasyPrint
        # Создаем заглушку изображения
        try:
            # Создаем простой файл заглушку
            image_content = self._create_mock_image(job, format)
            
            with open(file_path, 'wb') as f:
                f.write(image_content)
            
            return True, str(file_path), None
            
        except Exception as e:
            return False, None, f"Ошибка создания изображения: {str(e)}"
    
    def _create_mock_pdf(self, job: PrintJob, html_content: str) -> bytes:
        """
        Создание заглушки PDF файла.
        
        Args:
            job: Задание печати
            html_content: HTML контент
            
        Returns:
            bytes: Содержимое PDF файла
        """
        # Простая заглушка PDF
        pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Print Job {job.id}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
297
%%EOF"""
        
        return pdf_content.encode('utf-8')
    
    def _create_mock_image(self, job: PrintJob, format: PrintFormat) -> bytes:
        """
        Создание заглушки изображения.
        
        Args:
            job: Задание печати
            format: Формат изображения
            
        Returns:
            bytes: Содержимое изображения
        """
        # Простая заглушка изображения
        if format == PrintFormat.PNG:
            # Минимальный PNG файл (1x1 пиксель, прозрачный)
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        elif format == PrintFormat.JPG:
            # Минимальный JPEG файл
            return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        else:
            # SVG заглушка
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="white" stroke="black" stroke-width="2"/>
  <text x="50" y="50" text-anchor="middle" font-family="Arial" font-size="12">
    Print Job {job.id}
  </text>
</svg>'''
            return svg_content.encode('utf-8')
    
    async def validate_html(self, html_content: str) -> Tuple[bool, Optional[str]]:
        """
        Валидация HTML контента.
        
        Args:
            html_content: HTML контент
            
        Returns:
            Tuple[bool, Optional[str]]: (валидность, сообщение об ошибке)
        """
        try:
            # Простая валидация HTML
            if not html_content.strip():
                return False, "HTML контент не может быть пустым"
            
            # Проверяем базовые теги
            if '<html' not in html_content.lower() and '<body' not in html_content.lower():
                return False, "HTML должен содержать теги html или body"
            
            return True, None
            
        except Exception as e:
            return False, f"Ошибка валидации HTML: {str(e)}"
    
    async def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о файле.
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Optional[Dict[str, Any]]: Информация о файле
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "file_path": str(path),
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path.suffix,
                "exists": True
            }
            
        except Exception as e:
            return {
                "file_path": file_path,
                "exists": False,
                "error": str(e)
            }
    
    async def cleanup_old_files(self, days: int = 7) -> int:
        """
        Очистка старых файлов.
        
        Args:
            days: Количество дней для хранения
            
        Returns:
            int: Количество удаленных файлов
        """
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            deleted_count = 0
            
            for file_path in self.output_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception:
                        pass  # Игнорируем ошибки удаления отдельных файлов
            
            return deleted_count
            
        except Exception:
            return 0
