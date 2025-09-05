"""
Сервис для работы с шаблонами печати.

Содержит бизнес-логику для управления шаблонами.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.exc import IntegrityError

from app.models.print_models import PrintTemplate, PrintJobType


class TemplateService:
    """Сервис для работы с шаблонами печати."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_template(
        self,
        name: str,
        description: Optional[str],
        template_type: PrintJobType,
        html_template: str,
        css_styles: Optional[str] = None,
        category: Optional[str] = None,
        default_page_size: str = "A4",
        default_orientation: str = "portrait",
        default_quality: int = 300,
        template_variables: Optional[Dict[str, Any]] = None,
        required_fields: Optional[List[str]] = None,
        is_system: bool = False
    ) -> PrintTemplate:
        """
        Создание шаблона печати.
        
        Args:
            name: Название шаблона
            description: Описание шаблона
            template_type: Тип шаблона
            html_template: HTML шаблон
            css_styles: CSS стили
            category: Категория шаблона
            default_page_size: Размер страницы по умолчанию
            default_orientation: Ориентация по умолчанию
            default_quality: Качество по умолчанию
            template_variables: Переменные шаблона
            required_fields: Обязательные поля
            is_system: Системный шаблон
            
        Returns:
            PrintTemplate: Созданный шаблон
        """
        template = PrintTemplate(
            name=name,
            description=description,
            template_type=template_type,
            html_template=html_template,
            css_styles=css_styles,
            category=category,
            default_page_size=default_page_size,
            default_orientation=default_orientation,
            default_quality=default_quality,
            template_variables=template_variables,
            required_fields=required_fields,
            is_system=is_system
        )
        
        try:
            self.db.add(template)
            await self.db.commit()
            await self.db.refresh(template)
            return template
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Шаблон с таким именем уже существует")
    
    async def get_template_by_id(self, template_id: int) -> Optional[PrintTemplate]:
        """
        Получение шаблона по ID.
        
        Args:
            template_id: ID шаблона
            
        Returns:
            Optional[PrintTemplate]: Шаблон или None
        """
        result = await self.db.execute(
            select(PrintTemplate).where(PrintTemplate.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def get_template_by_name(self, name: str) -> Optional[PrintTemplate]:
        """
        Получение шаблона по имени.
        
        Args:
            name: Имя шаблона
            
        Returns:
            Optional[PrintTemplate]: Шаблон или None
        """
        result = await self.db.execute(
            select(PrintTemplate).where(PrintTemplate.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_templates(
        self,
        template_type: Optional[PrintJobType] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[PrintTemplate]:
        """
        Получение списка шаблонов.
        
        Args:
            template_type: Тип шаблона для фильтрации
            category: Категория для фильтрации
            is_active: Активность шаблона
            is_system: Системный шаблон
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[PrintTemplate]: Список шаблонов
        """
        query = select(PrintTemplate)
        conditions = []
        
        if template_type:
            conditions.append(PrintTemplate.template_type == template_type)
        if category:
            conditions.append(PrintTemplate.category == category)
        if is_active is not None:
            conditions.append(PrintTemplate.is_active == is_active)
        if is_system is not None:
            conditions.append(PrintTemplate.is_system == is_system)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PrintTemplate.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_active_templates(
        self,
        template_type: Optional[PrintJobType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[PrintTemplate]:
        """
        Получение активных шаблонов.
        
        Args:
            template_type: Тип шаблона для фильтрации
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[PrintTemplate]: Список активных шаблонов
        """
        query = select(PrintTemplate).where(PrintTemplate.is_active == True)
        
        if template_type:
            query = query.where(PrintTemplate.template_type == template_type)
        
        query = query.order_by(PrintTemplate.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        template_type: Optional[PrintJobType] = None,
        html_template: Optional[str] = None,
        css_styles: Optional[str] = None,
        category: Optional[str] = None,
        default_page_size: Optional[str] = None,
        default_orientation: Optional[str] = None,
        default_quality: Optional[int] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        required_fields: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[PrintTemplate]:
        """
        Обновление шаблона печати.
        
        Args:
            template_id: ID шаблона
            name: Название шаблона
            description: Описание шаблона
            template_type: Тип шаблона
            html_template: HTML шаблон
            css_styles: CSS стили
            category: Категория шаблона
            default_page_size: Размер страницы по умолчанию
            default_orientation: Ориентация по умолчанию
            default_quality: Качество по умолчанию
            template_variables: Переменные шаблона
            required_fields: Обязательные поля
            is_active: Активность шаблона
            
        Returns:
            Optional[PrintTemplate]: Обновленный шаблон или None
        """
        template = await self.get_template_by_id(template_id)
        if not template:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if template_type is not None:
            update_data["template_type"] = template_type
        if html_template is not None:
            update_data["html_template"] = html_template
        if css_styles is not None:
            update_data["css_styles"] = css_styles
        if category is not None:
            update_data["category"] = category
        if default_page_size is not None:
            update_data["default_page_size"] = default_page_size
        if default_orientation is not None:
            update_data["default_orientation"] = default_orientation
        if default_quality is not None:
            update_data["default_quality"] = default_quality
        if template_variables is not None:
            update_data["template_variables"] = template_variables
        if required_fields is not None:
            update_data["required_fields"] = required_fields
        if is_active is not None:
            update_data["is_active"] = is_active
        
        if not update_data:
            return template
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await self.db.execute(
                update(PrintTemplate)
                .where(PrintTemplate.id == template_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_template_by_id(template_id)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Шаблон с таким именем уже существует")
    
    async def delete_template(self, template_id: int) -> bool:
        """
        Удаление шаблона печати.
        
        Args:
            template_id: ID шаблона
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        template = await self.get_template_by_id(template_id)
        if not template:
            return False
        
        # Нельзя удалять системные шаблоны
        if template.is_system:
            raise ValueError("Нельзя удалять системные шаблоны")
        
        await self.db.execute(
            delete(PrintTemplate).where(PrintTemplate.id == template_id)
        )
        await self.db.commit()
        
        return True
    
    async def toggle_template_status(self, template_id: int) -> bool:
        """
        Переключение статуса активности шаблона.
        
        Args:
            template_id: ID шаблона
            
        Returns:
            bool: True если успешно, False иначе
        """
        template = await self.get_template_by_id(template_id)
        if not template:
            return False
        
        await self.db.execute(
            update(PrintTemplate)
            .where(PrintTemplate.id == template_id)
            .values(
                is_active=not template.is_active,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def validate_template(self, template: PrintTemplate) -> tuple[bool, Optional[str]]:
        """
        Валидация шаблона.
        
        Args:
            template: Шаблон для валидации
            
        Returns:
            tuple[bool, Optional[str]]: (валидность, сообщение об ошибке)
        """
        try:
            # Проверяем HTML
            if not template.html_template.strip():
                return False, "HTML шаблон не может быть пустым"
            
            # Проверяем обязательные поля
            if template.required_fields:
                for field in template.required_fields:
                    placeholder = f"{{{{{field}}}}}"
                    if placeholder not in template.html_template:
                        return False, f"Обязательное поле '{field}' не найдено в шаблоне"
            
            # Проверяем переменные
            if template.template_variables:
                for var_name in template.template_variables.keys():
                    placeholder = f"{{{{{var_name}}}}}"
                    if placeholder not in template.html_template:
                        return False, f"Переменная '{var_name}' не найдена в шаблоне"
            
            return True, None
            
        except Exception as e:
            return False, f"Ошибка валидации шаблона: {str(e)}"
    
    async def get_template_stats(self) -> Dict[str, Any]:
        """
        Получение статистики шаблонов.
        
        Returns:
            Dict[str, Any]: Статистика шаблонов
        """
        from sqlalchemy import func
        
        # Общее количество шаблонов
        total_templates_result = await self.db.execute(
            select(func.count(PrintTemplate.id))
        )
        total_templates = total_templates_result.scalar() or 0
        
        # Активные шаблоны
        active_templates_result = await self.db.execute(
            select(func.count(PrintTemplate.id))
            .where(PrintTemplate.is_active == True)
        )
        active_templates = active_templates_result.scalar() or 0
        
        # Шаблоны по типам
        templates_by_type_result = await self.db.execute(
            select(
                PrintTemplate.template_type,
                func.count(PrintTemplate.id).label('count')
            )
            .where(PrintTemplate.is_active == True)
            .group_by(PrintTemplate.template_type)
        )
        templates_by_type = {row.template_type.value: row.count for row in templates_by_type_result}
        
        # Шаблоны по категориям
        templates_by_category_result = await self.db.execute(
            select(
                PrintTemplate.category,
                func.count(PrintTemplate.id).label('count')
            )
            .where(PrintTemplate.is_active == True)
            .group_by(PrintTemplate.category)
        )
        templates_by_category = {row.category or "Без категории": row.count for row in templates_by_category_result}
        
        return {
            "total_templates": total_templates,
            "active_templates": active_templates,
            "templates_by_type": templates_by_type,
            "templates_by_category": templates_by_category
        }
