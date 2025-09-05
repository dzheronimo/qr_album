"""
Сервис для работы с макетами печати.

Содержит бизнес-логику для управления макетами.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.exc import IntegrityError

from app.models.print_models import PrintLayout, PrintJobType


class LayoutService:
    """Сервис для работы с макетами печати."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_layout(
        self,
        name: str,
        description: Optional[str],
        layout_type: PrintJobType,
        page_width: float,
        page_height: float,
        margin_top: float = 10.0,
        margin_bottom: float = 10.0,
        margin_left: float = 10.0,
        margin_right: float = 10.0,
        elements: Optional[Dict[str, Any]] = None,
        is_system: bool = False
    ) -> PrintLayout:
        """
        Создание макета печати.
        
        Args:
            name: Название макета
            description: Описание макета
            layout_type: Тип макета
            page_width: Ширина страницы (мм)
            page_height: Высота страницы (мм)
            margin_top: Верхний отступ (мм)
            margin_bottom: Нижний отступ (мм)
            margin_left: Левый отступ (мм)
            margin_right: Правый отступ (мм)
            elements: Элементы макета
            is_system: Системный макет
            
        Returns:
            PrintLayout: Созданный макет
        """
        layout = PrintLayout(
            name=name,
            description=description,
            layout_type=layout_type,
            page_width=page_width,
            page_height=page_height,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
            margin_left=margin_left,
            margin_right=margin_right,
            elements=elements or {},
            is_system=is_system
        )
        
        try:
            self.db.add(layout)
            await self.db.commit()
            await self.db.refresh(layout)
            return layout
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Макет с таким именем уже существует")
    
    async def get_layout_by_id(self, layout_id: int) -> Optional[PrintLayout]:
        """
        Получение макета по ID.
        
        Args:
            layout_id: ID макета
            
        Returns:
            Optional[PrintLayout]: Макет или None
        """
        result = await self.db.execute(
            select(PrintLayout).where(PrintLayout.id == layout_id)
        )
        return result.scalar_one_or_none()
    
    async def get_layout_by_name(self, name: str) -> Optional[PrintLayout]:
        """
        Получение макета по имени.
        
        Args:
            name: Имя макета
            
        Returns:
            Optional[PrintLayout]: Макет или None
        """
        result = await self.db.execute(
            select(PrintLayout).where(PrintLayout.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_layouts(
        self,
        layout_type: Optional[PrintJobType] = None,
        is_active: Optional[bool] = None,
        is_system: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[PrintLayout]:
        """
        Получение списка макетов.
        
        Args:
            layout_type: Тип макета для фильтрации
            is_active: Активность макета
            is_system: Системный макет
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[PrintLayout]: Список макетов
        """
        query = select(PrintLayout)
        conditions = []
        
        if layout_type:
            conditions.append(PrintLayout.layout_type == layout_type)
        if is_active is not None:
            conditions.append(PrintLayout.is_active == is_active)
        if is_system is not None:
            conditions.append(PrintLayout.is_system == is_system)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PrintLayout.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_active_layouts(
        self,
        layout_type: Optional[PrintJobType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[PrintLayout]:
        """
        Получение активных макетов.
        
        Args:
            layout_type: Тип макета для фильтрации
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[PrintLayout]: Список активных макетов
        """
        query = select(PrintLayout).where(PrintLayout.is_active == True)
        
        if layout_type:
            query = query.where(PrintLayout.layout_type == layout_type)
        
        query = query.order_by(PrintLayout.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_layout(
        self,
        layout_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        layout_type: Optional[PrintJobType] = None,
        page_width: Optional[float] = None,
        page_height: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_right: Optional[float] = None,
        elements: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None
    ) -> Optional[PrintLayout]:
        """
        Обновление макета печати.
        
        Args:
            layout_id: ID макета
            name: Название макета
            description: Описание макета
            layout_type: Тип макета
            page_width: Ширина страницы (мм)
            page_height: Высота страницы (мм)
            margin_top: Верхний отступ (мм)
            margin_bottom: Нижний отступ (мм)
            margin_left: Левый отступ (мм)
            margin_right: Правый отступ (мм)
            elements: Элементы макета
            is_active: Активность макета
            
        Returns:
            Optional[PrintLayout]: Обновленный макет или None
        """
        layout = await self.get_layout_by_id(layout_id)
        if not layout:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if layout_type is not None:
            update_data["layout_type"] = layout_type
        if page_width is not None:
            update_data["page_width"] = page_width
        if page_height is not None:
            update_data["page_height"] = page_height
        if margin_top is not None:
            update_data["margin_top"] = margin_top
        if margin_bottom is not None:
            update_data["margin_bottom"] = margin_bottom
        if margin_left is not None:
            update_data["margin_left"] = margin_left
        if margin_right is not None:
            update_data["margin_right"] = margin_right
        if elements is not None:
            update_data["elements"] = elements
        if is_active is not None:
            update_data["is_active"] = is_active
        
        if not update_data:
            return layout
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await self.db.execute(
                update(PrintLayout)
                .where(PrintLayout.id == layout_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_layout_by_id(layout_id)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Макет с таким именем уже существует")
    
    async def delete_layout(self, layout_id: int) -> bool:
        """
        Удаление макета печати.
        
        Args:
            layout_id: ID макета
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        layout = await self.get_layout_by_id(layout_id)
        if not layout:
            return False
        
        # Нельзя удалять системные макеты
        if layout.is_system:
            raise ValueError("Нельзя удалять системные макеты")
        
        await self.db.execute(
            delete(PrintLayout).where(PrintLayout.id == layout_id)
        )
        await self.db.commit()
        
        return True
    
    async def toggle_layout_status(self, layout_id: int) -> bool:
        """
        Переключение статуса активности макета.
        
        Args:
            layout_id: ID макета
            
        Returns:
            bool: True если успешно, False иначе
        """
        layout = await self.get_layout_by_id(layout_id)
        if not layout:
            return False
        
        await self.db.execute(
            update(PrintLayout)
            .where(PrintLayout.id == layout_id)
            .values(
                is_active=not layout.is_active,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def validate_layout(self, layout: PrintLayout) -> tuple[bool, Optional[str]]:
        """
        Валидация макета.
        
        Args:
            layout: Макет для валидации
            
        Returns:
            tuple[bool, Optional[str]]: (валидность, сообщение об ошибке)
        """
        try:
            # Проверяем размеры страницы
            if layout.page_width <= 0 or layout.page_height <= 0:
                return False, "Размеры страницы должны быть положительными"
            
            # Проверяем отступы
            if (layout.margin_left + layout.margin_right >= layout.page_width or
                layout.margin_top + layout.margin_bottom >= layout.page_height):
                return False, "Отступы не должны превышать размеры страницы"
            
            # Проверяем элементы макета
            if layout.elements:
                for element_name, element_data in layout.elements.items():
                    if not isinstance(element_data, dict):
                        return False, f"Элемент '{element_name}' должен быть словарем"
                    
                    # Проверяем обязательные поля элемента
                    required_fields = ["type", "x", "y", "width", "height"]
                    for field in required_fields:
                        if field not in element_data:
                            return False, f"Элемент '{element_name}' должен содержать поле '{field}'"
            
            return True, None
            
        except Exception as e:
            return False, f"Ошибка валидации макета: {str(e)}"
    
    async def get_layout_stats(self) -> Dict[str, Any]:
        """
        Получение статистики макетов.
        
        Returns:
            Dict[str, Any]: Статистика макетов
        """
        from sqlalchemy import func
        
        # Общее количество макетов
        total_layouts_result = await self.db.execute(
            select(func.count(PrintLayout.id))
        )
        total_layouts = total_layouts_result.scalar() or 0
        
        # Активные макеты
        active_layouts_result = await self.db.execute(
            select(func.count(PrintLayout.id))
            .where(PrintLayout.is_active == True)
        )
        active_layouts = active_layouts_result.scalar() or 0
        
        # Макеты по типам
        layouts_by_type_result = await self.db.execute(
            select(
                PrintLayout.layout_type,
                func.count(PrintLayout.id).label('count')
            )
            .where(PrintLayout.is_active == True)
            .group_by(PrintLayout.layout_type)
        )
        layouts_by_type = {row.layout_type.value: row.count for row in layouts_by_type_result}
        
        return {
            "total_layouts": total_layouts,
            "active_layouts": active_layouts,
            "layouts_by_type": layouts_by_type
        }
