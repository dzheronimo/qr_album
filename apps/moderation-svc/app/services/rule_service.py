"""
Сервис для работы с правилами модерации.

Содержит бизнес-логику для управления правилами модерации.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from sqlalchemy.exc import IntegrityError

from app.models.moderation import ModerationRule, ModerationRequest, ContentType


class RuleService:
    """Сервис для работы с правилами модерации."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    async def create_rule(
        self,
        name: str,
        description: Optional[str],
        content_type: ContentType,
        conditions: Dict[str, Any],
        action: str,
        threshold: Optional[float] = None,
        priority: int = 1,
        auto_action: bool = False
    ) -> ModerationRule:
        """
        Создание правила модерации.
        
        Args:
            name: Название правила
            description: Описание правила
            content_type: Тип контента
            conditions: Условия правила
            action: Действие при срабатывании
            threshold: Пороговое значение
            priority: Приоритет правила
            auto_action: Автоматическое действие
            
        Returns:
            ModerationRule: Созданное правило
        """
        rule = ModerationRule(
            name=name,
            description=description,
            content_type=content_type,
            conditions=conditions,
            action=action,
            threshold=threshold,
            priority=priority,
            auto_action=auto_action
        )
        
        try:
            self.db.add(rule)
            await self.db.commit()
            await self.db.refresh(rule)
            return rule
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Правило с таким именем уже существует")
    
    async def get_rule_by_id(self, rule_id: int) -> Optional[ModerationRule]:
        """
        Получение правила по ID.
        
        Args:
            rule_id: ID правила
            
        Returns:
            Optional[ModerationRule]: Правило или None
        """
        result = await self.db.execute(
            select(ModerationRule).where(ModerationRule.id == rule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_rule_by_name(self, name: str) -> Optional[ModerationRule]:
        """
        Получение правила по имени.
        
        Args:
            name: Имя правила
            
        Returns:
            Optional[ModerationRule]: Правило или None
        """
        result = await self.db.execute(
            select(ModerationRule).where(ModerationRule.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_active_rules(
        self,
        content_type: Optional[ContentType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ModerationRule]:
        """
        Получение активных правил.
        
        Args:
            content_type: Тип контента для фильтрации
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationRule]: Список правил
        """
        query = select(ModerationRule).where(ModerationRule.is_active == True)
        
        if content_type:
            query = query.where(ModerationRule.content_type == content_type)
        
        query = query.order_by(ModerationRule.priority.desc(), ModerationRule.created_at.asc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_all_rules(
        self,
        content_type: Optional[ContentType] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ModerationRule]:
        """
        Получение всех правил.
        
        Args:
            content_type: Тип контента для фильтрации
            is_active: Активность правила
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationRule]: Список правил
        """
        query = select(ModerationRule)
        
        conditions = []
        if content_type:
            conditions.append(ModerationRule.content_type == content_type)
        if is_active is not None:
            conditions.append(ModerationRule.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ModerationRule.priority.desc(), ModerationRule.created_at.asc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_rule(
        self,
        rule_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content_type: Optional[ContentType] = None,
        conditions: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
        threshold: Optional[float] = None,
        priority: Optional[int] = None,
        is_active: Optional[bool] = None,
        auto_action: Optional[bool] = None
    ) -> Optional[ModerationRule]:
        """
        Обновление правила модерации.
        
        Args:
            rule_id: ID правила
            name: Название правила
            description: Описание правила
            content_type: Тип контента
            conditions: Условия правила
            action: Действие при срабатывании
            threshold: Пороговое значение
            priority: Приоритет правила
            is_active: Активность правила
            auto_action: Автоматическое действие
            
        Returns:
            Optional[ModerationRule]: Обновленное правило или None
        """
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return None
        
        # Обновляем поля
        update_data = {}
        
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if content_type is not None:
            update_data["content_type"] = content_type
        if conditions is not None:
            update_data["conditions"] = conditions
        if action is not None:
            update_data["action"] = action
        if threshold is not None:
            update_data["threshold"] = threshold
        if priority is not None:
            update_data["priority"] = priority
        if is_active is not None:
            update_data["is_active"] = is_active
        if auto_action is not None:
            update_data["auto_action"] = auto_action
        
        if not update_data:
            return rule
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await self.db.execute(
                update(ModerationRule)
                .where(ModerationRule.id == rule_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_rule_by_id(rule_id)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Правило с таким именем уже существует")
    
    async def delete_rule(self, rule_id: int) -> bool:
        """
        Удаление правила модерации.
        
        Args:
            rule_id: ID правила
            
        Returns:
            bool: True если удаление успешно, False иначе
        """
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return False
        
        await self.db.execute(
            delete(ModerationRule).where(ModerationRule.id == rule_id)
        )
        await self.db.commit()
        
        return True
    
    async def toggle_rule_status(self, rule_id: int) -> bool:
        """
        Переключение статуса активности правила.
        
        Args:
            rule_id: ID правила
            
        Returns:
            bool: True если успешно, False иначе
        """
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return False
        
        await self.db.execute(
            update(ModerationRule)
            .where(ModerationRule.id == rule_id)
            .values(
                is_active=not rule.is_active,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
        
        return True
    
    async def evaluate_rule(
        self,
        rule: ModerationRule,
        request: ModerationRequest
    ) -> bool:
        """
        Оценка правила для запроса на модерацию.
        
        Args:
            rule: Правило модерации
            request: Запрос на модерацию
            
        Returns:
            bool: True если правило сработало, False иначе
        """
        try:
            conditions = rule.conditions
            
            # Проверяем тип контента
            if conditions.get("content_type") and conditions["content_type"] != request.content_type.value:
                return False
            
            # Проверяем условия в зависимости от типа контента
            if request.content_type == ContentType.TEXT:
                return await self._evaluate_text_conditions(conditions, request)
            elif request.content_type == ContentType.IMAGE:
                return await self._evaluate_image_conditions(conditions, request)
            elif request.content_type == ContentType.VIDEO:
                return await self._evaluate_video_conditions(conditions, request)
            else:
                return False
                
        except Exception:
            return False
    
    async def _evaluate_text_conditions(
        self,
        conditions: Dict[str, Any],
        request: ModerationRequest
    ) -> bool:
        """
        Оценка условий для текстового контента.
        
        Args:
            conditions: Условия правила
            request: Запрос на модерацию
            
        Returns:
            bool: True если условия выполнены
        """
        text = request.content_text or ""
        
        # Проверка на запрещенные слова
        if "forbidden_words" in conditions:
            forbidden_words = conditions["forbidden_words"]
            if any(word.lower() in text.lower() for word in forbidden_words):
                return True
        
        # Проверка длины текста
        if "min_length" in conditions:
            if len(text) < conditions["min_length"]:
                return True
        
        if "max_length" in conditions:
            if len(text) > conditions["max_length"]:
                return True
        
        # Проверка на спам (повторяющиеся слова)
        if "spam_detection" in conditions and conditions["spam_detection"]:
            words = text.split()
            if len(words) > 10:
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                
                max_repetition = max(word_counts.values()) if word_counts else 0
                if max_repetition > len(words) * 0.3:
                    return True
        
        return False
    
    async def _evaluate_image_conditions(
        self,
        conditions: Dict[str, Any],
        request: ModerationRequest
    ) -> bool:
        """
        Оценка условий для изображений.
        
        Args:
            conditions: Условия правила
            request: Запрос на модерацию
            
        Returns:
            bool: True если условия выполнены
        """
        metadata = request.content_metadata or {}
        
        # Проверка размера файла
        if "max_file_size" in conditions:
            file_size = metadata.get("file_size", 0)
            if file_size > conditions["max_file_size"]:
                return True
        
        # Проверка разрешения
        if "max_resolution" in conditions:
            dimensions = metadata.get("dimensions", "0x0")
            try:
                width, height = map(int, dimensions.split("x"))
                max_width, max_height = conditions["max_resolution"]
                if width > max_width or height > max_height:
                    return True
            except (ValueError, IndexError):
                pass
        
        # Проверка формата файла
        if "allowed_formats" in conditions:
            file_format = metadata.get("format", "").lower()
            if file_format not in conditions["allowed_formats"]:
                return True
        
        return False
    
    async def _evaluate_video_conditions(
        self,
        conditions: Dict[str, Any],
        request: ModerationRequest
    ) -> bool:
        """
        Оценка условий для видео.
        
        Args:
            conditions: Условия правила
            request: Запрос на модерацию
            
        Returns:
            bool: True если условия выполнены
        """
        metadata = request.content_metadata or {}
        
        # Проверка длительности
        if "max_duration" in conditions:
            duration = metadata.get("duration", 0)
            if duration > conditions["max_duration"]:
                return True
        
        # Проверка размера файла
        if "max_file_size" in conditions:
            file_size = metadata.get("file_size", 0)
            if file_size > conditions["max_file_size"]:
                return True
        
        # Проверка разрешения
        if "max_resolution" in conditions:
            resolution = metadata.get("resolution", "0x0")
            try:
                width, height = map(int, resolution.split("x"))
                max_width, max_height = conditions["max_resolution"]
                if width > max_width or height > max_height:
                    return True
            except (ValueError, IndexError):
                pass
        
        return False
    
    async def get_rule_stats(self) -> Dict[str, Any]:
        """
        Получение статистики правил.
        
        Returns:
            Dict[str, Any]: Статистика правил
        """
        from sqlalchemy import func
        
        # Общее количество правил
        total_rules_result = await self.db.execute(
            select(func.count(ModerationRule.id))
        )
        total_rules = total_rules_result.scalar() or 0
        
        # Активные правила
        active_rules_result = await self.db.execute(
            select(func.count(ModerationRule.id))
            .where(ModerationRule.is_active == True)
        )
        active_rules = active_rules_result.scalar() or 0
        
        # Правила по типам контента
        rules_by_type_result = await self.db.execute(
            select(
                ModerationRule.content_type,
                func.count(ModerationRule.id).label('count')
            )
            .where(ModerationRule.is_active == True)
            .group_by(ModerationRule.content_type)
        )
        rules_by_type = {row.content_type.value: row.count for row in rules_by_type_result}
        
        # Правила по действиям
        rules_by_action_result = await self.db.execute(
            select(
                ModerationRule.action,
                func.count(ModerationRule.id).label('count')
            )
            .where(ModerationRule.is_active == True)
            .group_by(ModerationRule.action)
        )
        rules_by_action = {row.action: row.count for row in rules_by_action_result}
        
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "rules_by_content_type": rules_by_type,
            "rules_by_action": rules_by_action
        }
