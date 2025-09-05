"""
Сервис для работы с печатью и PDF генерацией.

Содержит основную бизнес-логику для управления заданиями печати.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.print_models import (
    PrintJob, PrintTemplate, PrintLayout, PrintQueue, PrintHistory,
    PrintJobStatus, PrintJobType, PrintFormat
)
from app.services.weasyprint_service import WeasyPrintService
from app.services.template_service import TemplateService
from app.services.layout_service import LayoutService
from app.services.queue_service import QueueService


class PrintService:
    """Сервис для работы с печатью и PDF генерацией."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.weasyprint_service = WeasyPrintService(db)
        self.template_service = TemplateService(db)
        self.layout_service = LayoutService(db)
        self.queue_service = QueueService(db)
    
    async def create_print_job(
        self,
        user_id: int,
        job_type: PrintJobType,
        content_data: Dict[str, Any],
        template_id: Optional[int] = None,
        layout_id: Optional[int] = None,
        print_format: PrintFormat = PrintFormat.PDF,
        page_size: str = "A4",
        orientation: str = "portrait",
        quality: int = 300,
        priority: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PrintJob:
        """
        Создание задания печати.
        
        Args:
            user_id: ID пользователя
            job_type: Тип задания печати
            content_data: Данные контента для печати
            template_id: ID шаблона
            layout_id: ID макета
            print_format: Формат печати
            page_size: Размер страницы
            orientation: Ориентация страницы
            quality: Качество (DPI)
            priority: Приоритет (1-5)
            metadata: Дополнительные метаданные
            
        Returns:
            PrintJob: Созданное задание
        """
        job = PrintJob(
            user_id=user_id,
            job_type=job_type,
            template_id=template_id,
            layout_id=layout_id,
            content_data=content_data,
            print_format=print_format,
            page_size=page_size,
            orientation=orientation,
            quality=quality,
            priority=priority,
            metadata=metadata
        )
        
        try:
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)
            
            # Добавляем в очередь
            await self.queue_service.add_to_queue(job.id, priority)
            
            # Логируем создание задания
            await self._log_job_action(
                job_id=job.id,
                action="created",
                actor_type="user",
                actor_id=user_id,
                message=f"Print job created for {job_type.value}"
            )
            
            return job
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании задания печати")
    
    async def process_print_job(
        self,
        job_id: int,
        worker_id: Optional[str] = None
    ) -> bool:
        """
        Обработка задания печати.
        
        Args:
            job_id: ID задания
            worker_id: ID воркера
            
        Returns:
            bool: True если успешно, False иначе
        """
        job = await self.get_print_job(job_id)
        if not job:
            return False
        
        try:
            # Обновляем статус на "обрабатывается"
            await self.update_job_status(job_id, PrintJobStatus.PROCESSING, worker_id=worker_id)
            
            # Получаем шаблон и макет
            template = None
            layout = None
            
            if job.template_id:
                template = await self.template_service.get_template_by_id(job.template_id)
            
            if job.layout_id:
                layout = await self.layout_service.get_layout_by_id(job.layout_id)
            
            # Генерируем HTML контент
            html_content, css_content = await self._generate_html_content(job, template, layout)
            
            # Валидируем HTML
            is_valid, error_message = await self.weasyprint_service.validate_html(html_content)
            if not is_valid:
                await self.update_job_status(job_id, PrintJobStatus.FAILED, error_message=error_message)
                return False
            
            # Генерируем файл
            success = False
            output_path = None
            error_message = None
            
            if job.print_format == PrintFormat.PDF:
                success, output_path, error_message = await self.weasyprint_service.generate_pdf(
                    job, html_content, css_content
                )
            else:
                success, output_path, error_message = await self.weasyprint_service.generate_image(
                    job, html_content, css_content, job.print_format
                )
            
            if success and output_path:
                # Получаем информацию о файле
                file_info = await self.weasyprint_service.get_file_info(output_path)
                
                # Обновляем задание с результатами
                await self._update_job_with_results(
                    job_id, 
                    output_path, 
                    file_info.get("file_size") if file_info else None,
                    error_message
                )
                
                # Логируем успешное завершение
                await self._log_job_action(
                    job_id=job_id,
                    action="completed",
                    actor_type="worker",
                    message=f"Print job completed successfully. Output: {output_path}"
                )
                
                return True
            else:
                # Логируем ошибку
                await self.update_job_status(job_id, PrintJobStatus.FAILED, error_message=error_message)
                await self._log_job_action(
                    job_id=job_id,
                    action="failed",
                    actor_type="worker",
                    message=f"Print job failed: {error_message}"
                )
                
                return False
                
        except Exception as e:
            # Логируем исключение
            await self.update_job_status(job_id, PrintJobStatus.FAILED, error_message=str(e))
            await self._log_job_action(
                job_id=job_id,
                action="error",
                actor_type="system",
                message=f"Print job processing error: {str(e)}"
            )
            return False
    
    async def _generate_html_content(
        self,
        job: PrintJob,
        template: Optional[PrintTemplate],
        layout: Optional[PrintLayout]
    ) -> tuple[str, Optional[str]]:
        """
        Генерация HTML контента для печати.
        
        Args:
            job: Задание печати
            template: Шаблон
            layout: Макет
            
        Returns:
            tuple[str, Optional[str]]: (HTML контент, CSS стили)
        """
        # Если есть шаблон, используем его
        if template:
            html_content = template.html_template
            css_content = template.css_styles
            
            # Заменяем переменные в шаблоне
            html_content = self._replace_template_variables(html_content, job.content_data)
            if css_content:
                css_content = self._replace_template_variables(css_content, job.content_data)
        else:
            # Генерируем базовый HTML на основе типа задания
            html_content, css_content = self._generate_default_html(job)
        
        # Применяем настройки макета
        if layout:
            html_content = self._apply_layout_settings(html_content, layout)
        
        return html_content, css_content
    
    def _replace_template_variables(
        self,
        content: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Замена переменных в шаблоне.
        
        Args:
            content: Контент с переменными
            data: Данные для замены
            
        Returns:
            str: Контент с замененными переменными
        """
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _generate_default_html(self, job: PrintJob) -> tuple[str, str]:
        """
        Генерация HTML по умолчанию.
        
        Args:
            job: Задание печати
            
        Returns:
            tuple[str, str]: (HTML контент, CSS стили)
        """
        if job.job_type == PrintJobType.QR_LABEL:
            return self._generate_qr_label_html(job)
        elif job.job_type == PrintJobType.ALBUM_COVER:
            return self._generate_album_cover_html(job)
        elif job.job_type == PrintJobType.PAGE_THUMBNAIL:
            return self._generate_page_thumbnail_html(job)
        else:
            return self._generate_custom_html(job)
    
    def _generate_qr_label_html(self, job: PrintJob) -> tuple[str, str]:
        """Генерация HTML для QR этикетки."""
        qr_data = job.content_data
        qr_code_url = qr_data.get("qr_code_url", "")
        title = qr_data.get("title", "QR Code")
        description = qr_data.get("description", "")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>
        <body>
            <div class="qr-label">
                <h1>{title}</h1>
                <div class="qr-code">
                    <img src="{qr_code_url}" alt="QR Code" />
                </div>
                <p class="description">{description}</p>
            </div>
        </body>
        </html>
        """
        
        css = """
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .qr-label {
            text-align: center;
            max-width: 300px;
            margin: 0 auto;
        }
        .qr-code img {
            max-width: 200px;
            height: auto;
        }
        .description {
            margin-top: 10px;
            font-size: 12px;
            color: #666;
        }
        """
        
        return html, css
    
    def _generate_album_cover_html(self, job: PrintJob) -> tuple[str, str]:
        """Генерация HTML для обложки альбома."""
        album_data = job.content_data
        title = album_data.get("title", "Album")
        subtitle = album_data.get("subtitle", "")
        cover_image = album_data.get("cover_image", "")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>
        <body>
            <div class="album-cover">
                <div class="cover-image">
                    <img src="{cover_image}" alt="Album Cover" />
                </div>
                <div class="cover-text">
                    <h1>{title}</h1>
                    <h2>{subtitle}</h2>
                </div>
            </div>
        </body>
        </html>
        """
        
        css = """
        body {
            margin: 0;
            padding: 0;
        }
        .album-cover {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .cover-image img {
            max-width: 300px;
            max-height: 300px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .cover-text {
            text-align: center;
            margin-top: 20px;
        }
        .cover-text h1 {
            font-size: 2.5em;
            margin: 0;
        }
        .cover-text h2 {
            font-size: 1.2em;
            margin: 10px 0 0 0;
            opacity: 0.8;
        }
        """
        
        return html, css
    
    def _generate_page_thumbnail_html(self, job: PrintJob) -> tuple[str, str]:
        """Генерация HTML для миниатюры страницы."""
        page_data = job.content_data
        title = page_data.get("title", "Page")
        thumbnail_image = page_data.get("thumbnail_image", "")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
        </head>
        <body>
            <div class="page-thumbnail">
                <div class="thumbnail-image">
                    <img src="{thumbnail_image}" alt="Page Thumbnail" />
                </div>
                <div class="thumbnail-title">
                    <h3>{title}</h3>
                </div>
            </div>
        </body>
        </html>
        """
        
        css = """
        body {
            margin: 0;
            padding: 10px;
        }
        .page-thumbnail {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            text-align: center;
            max-width: 200px;
        }
        .thumbnail-image img {
            max-width: 150px;
            max-height: 150px;
            border-radius: 3px;
        }
        .thumbnail-title h3 {
            margin: 10px 0 0 0;
            font-size: 14px;
            color: #333;
        }
        """
        
        return html, css
    
    def _generate_custom_html(self, job: PrintJob) -> tuple[str, str]:
        """Генерация HTML для пользовательского шаблона."""
        custom_data = job.content_data
        content = custom_data.get("content", "Custom Content")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Custom Print</title>
        </head>
        <body>
            <div class="custom-content">
                {content}
            </div>
        </body>
        </html>
        """
        
        css = """
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 0;
        }
        .custom-content {
            max-width: 800px;
            margin: 0 auto;
        }
        """
        
        return html, css
    
    def _apply_layout_settings(self, html_content: str, layout: PrintLayout) -> str:
        """
        Применение настроек макета к HTML.
        
        Args:
            html_content: HTML контент
            layout: Макет
            
        Returns:
            str: HTML с примененными настройками макета
        """
        # Добавляем стили макета в HTML
        layout_css = f"""
        <style>
        @page {{
            size: {layout.page_width}mm {layout.page_height}mm;
            margin: {layout.margin_top}mm {layout.margin_right}mm {layout.margin_bottom}mm {layout.margin_left}mm;
        }}
        body {{
            width: {layout.page_width - layout.margin_left - layout.margin_right}mm;
            height: {layout.page_height - layout.margin_top - layout.margin_bottom}mm;
        }}
        </style>
        """
        
        # Вставляем CSS в head
        if "<head>" in html_content:
            html_content = html_content.replace("<head>", f"<head>{layout_css}")
        else:
            html_content = f"<head>{layout_css}</head>{html_content}"
        
        return html_content
    
    async def get_print_job(self, job_id: int) -> Optional[PrintJob]:
        """
        Получение задания печати по ID.
        
        Args:
            job_id: ID задания
            
        Returns:
            Optional[PrintJob]: Задание или None
        """
        result = await self.db.execute(
            select(PrintJob).where(PrintJob.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_print_jobs(
        self,
        user_id: int,
        job_type: Optional[PrintJobType] = None,
        status: Optional[PrintJobStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[PrintJob]:
        """
        Получение заданий печати пользователя.
        
        Args:
            user_id: ID пользователя
            job_type: Тип задания для фильтрации
            status: Статус для фильтрации
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[PrintJob]: Список заданий
        """
        query = select(PrintJob).where(PrintJob.user_id == user_id)
        
        if job_type:
            query = query.where(PrintJob.job_type == job_type)
        if status:
            query = query.where(PrintJob.status == status)
        
        query = query.order_by(PrintJob.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_job_status(
        self,
        job_id: int,
        status: PrintJobStatus,
        progress: Optional[int] = None,
        error_message: Optional[str] = None,
        worker_id: Optional[str] = None
    ) -> bool:
        """
        Обновление статуса задания.
        
        Args:
            job_id: ID задания
            status: Новый статус
            progress: Прогресс (0-100)
            error_message: Сообщение об ошибке
            worker_id: ID воркера
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            if progress is not None:
                update_data["progress"] = progress
            
            if error_message:
                update_data["error_message"] = error_message
            
            if status == PrintJobStatus.PROCESSING and not worker_id:
                update_data["started_at"] = datetime.utcnow()
            elif status in [PrintJobStatus.COMPLETED, PrintJobStatus.FAILED]:
                update_data["completed_at"] = datetime.utcnow()
            
            await self.db.execute(
                update(PrintJob)
                .where(PrintJob.id == job_id)
                .values(**update_data)
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def _update_job_with_results(
        self,
        job_id: int,
        output_path: str,
        file_size: Optional[int],
        error_message: Optional[str]
    ) -> None:
        """
        Обновление задания с результатами.
        
        Args:
            job_id: ID задания
            output_path: Путь к выходному файлу
            file_size: Размер файла
            error_message: Сообщение об ошибке
        """
        status = PrintJobStatus.COMPLETED if not error_message else PrintJobStatus.FAILED
        
        update_data = {
            "status": status,
            "output_file_path": output_path,
            "output_file_size": file_size,
            "progress": 100,
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if error_message:
            update_data["error_message"] = error_message
        
        await self.db.execute(
            update(PrintJob)
            .where(PrintJob.id == job_id)
            .values(**update_data)
        )
        await self.db.commit()
    
    async def _log_job_action(
        self,
        job_id: int,
        action: str,
        actor_type: str,
        actor_id: Optional[int] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Логирование действия с заданием.
        
        Args:
            job_id: ID задания
            action: Действие
            actor_type: Тип исполнителя
            actor_id: ID исполнителя
            message: Сообщение
            details: Детали
        """
        history = PrintHistory(
            job_id=job_id,
            action=action,
            actor_type=actor_type,
            actor_id=actor_id,
            message=message,
            details=details
        )
        
        self.db.add(history)
        await self.db.commit()
    
    async def get_print_stats(self) -> Dict[str, Any]:
        """
        Получение статистики печати.
        
        Returns:
            Dict[str, Any]: Статистика печати
        """
        # Общее количество заданий
        total_jobs_result = await self.db.execute(
            select(func.count(PrintJob.id))
        )
        total_jobs = total_jobs_result.scalar() or 0
        
        # Задания по статусам
        jobs_by_status_result = await self.db.execute(
            select(
                PrintJob.status,
                func.count(PrintJob.id).label('count')
            )
            .group_by(PrintJob.status)
        )
        jobs_by_status = {row.status.value: row.count for row in jobs_by_status_result}
        
        # Задания по типам
        jobs_by_type_result = await self.db.execute(
            select(
                PrintJob.job_type,
                func.count(PrintJob.id).label('count')
            )
            .group_by(PrintJob.job_type)
        )
        jobs_by_type = {row.job_type.value: row.count for row in jobs_by_type_result}
        
        # Задания по форматам
        jobs_by_format_result = await self.db.execute(
            select(
                PrintJob.print_format,
                func.count(PrintJob.id).label('count')
            )
            .group_by(PrintJob.print_format)
        )
        jobs_by_format = {row.print_format.value: row.count for row in jobs_by_format_result}
        
        return {
            "total_jobs": total_jobs,
            "jobs_by_status": jobs_by_status,
            "jobs_by_type": jobs_by_type,
            "jobs_by_format": jobs_by_format
        }
