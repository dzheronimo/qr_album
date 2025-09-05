"""
Сервис для работы с модерацией контента.

Содержит основную бизнес-логику для модерации.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.exc import IntegrityError

from app.models.moderation import (
    ModerationRequest, ModerationResult, ModerationRule, 
    ContentType, ModerationStatus, ModerationType, SeverityLevel
)
from app.services.ai_service import AIService
from app.services.rule_service import RuleService
from app.services.log_service import LogService


class ModerationService:
    """Сервис для работы с модерацией контента."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.ai_service = AIService(db)
        self.rule_service = RuleService(db)
        self.log_service = LogService(db)
    
    async def create_moderation_request(
        self,
        user_id: int,
        content_type: ContentType,
        content_id: Optional[str] = None,
        content_url: Optional[str] = None,
        content_text: Optional[str] = None,
        content_metadata: Optional[Dict[str, Any]] = None,
        moderation_type: ModerationType = ModerationType.AUTOMATIC,
        priority: int = 1,
        context: Optional[str] = None,
        source: Optional[str] = None
    ) -> ModerationRequest:
        """
        Создание запроса на модерацию.
        
        Args:
            user_id: ID пользователя
            content_type: Тип контента
            content_id: ID контента
            content_url: URL контента
            content_text: Текстовое содержимое
            content_metadata: Метаданные контента
            moderation_type: Тип модерации
            priority: Приоритет (1-5)
            context: Контекст запроса
            source: Источник запроса
            
        Returns:
            ModerationRequest: Созданный запрос
        """
        request = ModerationRequest(
            user_id=user_id,
            content_type=content_type,
            content_id=content_id,
            content_url=content_url,
            content_text=content_text,
            content_metadata=content_metadata,
            moderation_type=moderation_type,
            priority=priority,
            context=context,
            source=source
        )
        
        try:
            self.db.add(request)
            await self.db.commit()
            await self.db.refresh(request)
            
            # Логируем создание запроса
            await self.log_service.log_action(
                request_id=request.id,
                action="created",
                actor_type="system",
                message=f"Moderation request created for {content_type.value} content"
            )
            
            return request
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Ошибка при создании запроса на модерацию")
    
    async def process_moderation_request(
        self,
        request_id: int,
        moderator_id: Optional[int] = None
    ) -> Optional[ModerationResult]:
        """
        Обработка запроса на модерацию.
        
        Args:
            request_id: ID запроса
            moderator_id: ID модератора (для ручной модерации)
            
        Returns:
            Optional[ModerationResult]: Результат модерации
        """
        request = await self.get_moderation_request(request_id)
        if not request:
            return None
        
        # Обновляем статус на "в обработке"
        await self.update_request_status(request_id, ModerationStatus.UNDER_REVIEW)
        
        try:
            result = None
            
            if request.moderation_type == ModerationType.AUTOMATIC:
                result = await self._process_automatic_moderation(request)
            elif request.moderation_type == ModerationType.AI:
                result = await self._process_ai_moderation(request)
            elif request.moderation_type == ModerationType.MANUAL:
                result = await self._process_manual_moderation(request, moderator_id)
            elif request.moderation_type == ModerationType.HYBRID:
                result = await self._process_hybrid_moderation(request, moderator_id)
            
            if result:
                # Обновляем статус запроса
                new_status = ModerationStatus.APPROVED if result.is_approved else ModerationStatus.REJECTED
                await self.update_request_status(request_id, new_status)
                
                # Логируем результат
                action = "approved" if result.is_approved else "rejected"
                await self.log_service.log_action(
                    request_id=request_id,
                    action=action,
                    actor_type="ai" if result.ai_model else "moderator",
                    actor_id=moderator_id,
                    message=f"Content {action} with confidence {result.confidence_score}"
                )
            
            return result
            
        except Exception as e:
            # В случае ошибки помечаем как отклоненный
            await self.update_request_status(request_id, ModerationStatus.REJECTED)
            await self.log_service.log_action(
                request_id=request_id,
                action="error",
                actor_type="system",
                message=f"Moderation processing error: {str(e)}"
            )
            return None
    
    async def _process_automatic_moderation(
        self,
        request: ModerationRequest
    ) -> Optional[ModerationResult]:
        """
        Автоматическая модерация на основе правил.
        
        Args:
            request: Запрос на модерацию
            
        Returns:
            Optional[ModerationResult]: Результат модерации
        """
        # Получаем активные правила для данного типа контента
        rules = await self.rule_service.get_active_rules(request.content_type)
        
        violations = []
        violation_categories = []
        risk_score = 0.0
        
        # Применяем правила
        for rule in rules:
            if await self.rule_service.evaluate_rule(rule, request):
                violations.append({
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "action": rule.action
                })
                violation_categories.append(rule.name)
                risk_score += 0.3  # Каждое нарушение увеличивает риск
        
        # Определяем результат
        is_approved = risk_score < 0.5
        confidence_score = min(0.9, 0.7 + abs(risk_score - 0.5))
        
        result = ModerationResult(
            request_id=request.id,
            is_approved=is_approved,
            confidence_score=confidence_score,
            risk_score=risk_score,
            violations=violations,
            violation_categories=violation_categories,
            severity_level=SeverityLevel.MEDIUM if risk_score > 0.5 else SeverityLevel.LOW
        )
        
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        
        return result
    
    async def _process_ai_moderation(
        self,
        request: ModerationRequest
    ) -> Optional[ModerationResult]:
        """
        AI модерация.
        
        Args:
            request: Запрос на модерацию
            
        Returns:
            Optional[ModerationResult]: Результат модерации
        """
        return await self.ai_service.analyze_content(request)
    
    async def _process_manual_moderation(
        self,
        request: ModerationRequest,
        moderator_id: Optional[int]
    ) -> Optional[ModerationResult]:
        """
        Ручная модерация.
        
        Args:
            request: Запрос на модерацию
            moderator_id: ID модератора
            
        Returns:
            Optional[ModerationResult]: Результат модерации
        """
        # Для ручной модерации создаем пустой результат
        # Модератор должен будет его заполнить через API
        result = ModerationResult(
            request_id=request.id,
            is_approved=False,  # По умолчанию отклонено до ручной проверки
            confidence_score=0.0,
            risk_score=0.5,
            moderator_id=moderator_id,
            human_override=True
        )
        
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        
        return result
    
    async def _process_hybrid_moderation(
        self,
        request: ModerationRequest,
        moderator_id: Optional[int]
    ) -> Optional[ModerationResult]:
        """
        Гибридная модерация (AI + правила + ручная проверка).
        
        Args:
            request: Запрос на модерацию
            moderator_id: ID модератора
            
        Returns:
            Optional[ModerationResult]: Результат модерации
        """
        # Сначала AI анализ
        ai_result = await self.ai_service.analyze_content(request)
        
        # Затем проверка правил
        rules_result = await self._process_automatic_moderation(request)
        
        # Объединяем результаты
        if ai_result and rules_result:
            # Если оба результата согласны, принимаем решение
            if ai_result.is_approved == rules_result.is_approved:
                final_result = ai_result
                final_result.confidence_score = (ai_result.confidence_score + rules_result.confidence_score) / 2
            else:
                # Если результаты расходятся, требуется ручная проверка
                final_result = ModerationResult(
                    request_id=request.id,
                    is_approved=False,
                    confidence_score=0.5,
                    risk_score=max(ai_result.risk_score, rules_result.risk_score),
                    violations=ai_result.violations + rules_result.violations,
                    violation_categories=list(set(
                        (ai_result.violation_categories or []) + 
                        (rules_result.violation_categories or [])
                    )),
                    moderator_id=moderator_id,
                    human_override=True
                )
                self.db.add(final_result)
                await self.db.commit()
                await self.db.refresh(final_result)
        else:
            final_result = ai_result or rules_result
        
        return final_result
    
    async def get_moderation_request(self, request_id: int) -> Optional[ModerationRequest]:
        """
        Получение запроса на модерацию по ID.
        
        Args:
            request_id: ID запроса
            
        Returns:
            Optional[ModerationRequest]: Запрос или None
        """
        result = await self.db.execute(
            select(ModerationRequest).where(ModerationRequest.id == request_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_moderation_requests(
        self,
        user_id: int,
        content_type: Optional[ContentType] = None,
        status: Optional[ModerationStatus] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ModerationRequest]:
        """
        Получение запросов на модерацию пользователя.
        
        Args:
            user_id: ID пользователя
            content_type: Тип контента для фильтрации
            status: Статус для фильтрации
            skip: Количество пропускаемых записей
            limit: Лимит записей
            
        Returns:
            List[ModerationRequest]: Список запросов
        """
        query = select(ModerationRequest).where(ModerationRequest.user_id == user_id)
        
        if content_type:
            query = query.where(ModerationRequest.content_type == content_type)
        if status:
            query = query.where(ModerationRequest.status == status)
        
        query = query.order_by(ModerationRequest.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_request_status(
        self,
        request_id: int,
        status: ModerationStatus
    ) -> bool:
        """
        Обновление статуса запроса.
        
        Args:
            request_id: ID запроса
            status: Новый статус
            
        Returns:
            bool: True если успешно, False иначе
        """
        try:
            await self.db.execute(
                update(ModerationRequest)
                .where(ModerationRequest.id == request_id)
                .values(
                    status=status,
                    updated_at=datetime.utcnow(),
                    processed_at=datetime.utcnow() if status in [ModerationStatus.APPROVED, ModerationStatus.REJECTED] else None
                )
            )
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_pending_requests(
        self,
        limit: int = 100
    ) -> List[ModerationRequest]:
        """
        Получение запросов, ожидающих обработки.
        
        Args:
            limit: Лимит записей
            
        Returns:
            List[ModerationRequest]: Список запросов
        """
        result = await self.db.execute(
            select(ModerationRequest)
            .where(ModerationRequest.status == ModerationStatus.PENDING)
            .order_by(ModerationRequest.priority.desc(), ModerationRequest.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_moderation_stats(self) -> Dict[str, Any]:
        """
        Получение статистики модерации.
        
        Returns:
            Dict[str, Any]: Статистика модерации
        """
        # Общее количество запросов
        total_requests_result = await self.db.execute(
            select(func.count(ModerationRequest.id))
        )
        total_requests = total_requests_result.scalar() or 0
        
        # Запросы по статусам
        requests_by_status_result = await self.db.execute(
            select(
                ModerationRequest.status,
                func.count(ModerationRequest.id).label('count')
            )
            .group_by(ModerationRequest.status)
        )
        requests_by_status = {row.status.value: row.count for row in requests_by_status_result}
        
        # Запросы по типам контента
        requests_by_type_result = await self.db.execute(
            select(
                ModerationRequest.content_type,
                func.count(ModerationRequest.id).label('count')
            )
            .group_by(ModerationRequest.content_type)
        )
        requests_by_type = {row.content_type.value: row.count for row in requests_by_type_result}
        
        # Запросы по типам модерации
        requests_by_moderation_type_result = await self.db.execute(
            select(
                ModerationRequest.moderation_type,
                func.count(ModerationRequest.id).label('count')
            )
            .group_by(ModerationRequest.moderation_type)
        )
        requests_by_moderation_type = {row.moderation_type.value: row.count for row in requests_by_moderation_type_result}
        
        # Статистика AI
        ai_stats = await self.ai_service.get_ai_stats()
        
        return {
            "total_requests": total_requests,
            "requests_by_status": requests_by_status,
            "requests_by_content_type": requests_by_type,
            "requests_by_moderation_type": requests_by_moderation_type,
            "ai_stats": ai_stats
        }
