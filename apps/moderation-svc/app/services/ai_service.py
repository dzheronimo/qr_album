"""
Сервис для работы с AI модерацией.

Содержит интеграцию с AI сервисами для анализа контента.
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.moderation import (
    ModerationRequest, ModerationResult, ContentType, 
    ModerationStatus, SeverityLevel
)


class AIService:
    """Сервис для работы с AI модерацией."""
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        self.ai_models = {
            "text": "text-moderation-v1",
            "image": "image-moderation-v1", 
            "video": "video-moderation-v1"
        }
    
    async def analyze_content(
        self,
        request: ModerationRequest
    ) -> Optional[ModerationResult]:
        """
        Анализ контента с помощью AI.
        
        Args:
            request: Запрос на модерацию
            
        Returns:
            Optional[ModerationResult]: Результат анализа или None
        """
        start_time = time.time()
        
        try:
            # Выбираем модель в зависимости от типа контента
            model = self.ai_models.get(request.content_type.value)
            if not model:
                return None
            
            # В реальном приложении здесь была бы интеграция с AI API
            # Для демонстрации используем заглушку
            analysis_result = await self._mock_ai_analysis(request)
            
            if not analysis_result:
                return None
            
            # Создаем результат модерации
            processing_time = int((time.time() - start_time) * 1000)
            
            result = ModerationResult(
                request_id=request.id,
                is_approved=analysis_result["is_approved"],
                confidence_score=analysis_result["confidence_score"],
                risk_score=analysis_result["risk_score"],
                violations=analysis_result["violations"],
                violation_categories=analysis_result["violation_categories"],
                severity_level=analysis_result.get("severity_level"),
                ai_model=model,
                ai_version="1.0.0",
                ai_analysis=analysis_result["detailed_analysis"],
                processing_time_ms=processing_time
            )
            
            self.db.add(result)
            await self.db.commit()
            await self.db.refresh(result)
            
            return result
            
        except Exception as e:
            # В случае ошибки логируем и возвращаем None
            print(f"AI analysis error: {str(e)}")
            return None
    
    async def _mock_ai_analysis(
        self,
        request: ModerationRequest
    ) -> Optional[Dict[str, Any]]:
        """
        Заглушка для AI анализа.
        
        Args:
            request: Запрос на модерацию
            
        Returns:
            Optional[Dict[str, Any]]: Результат анализа
        """
        # Имитируем задержку AI обработки
        await asyncio.sleep(0.1)
        
        # Простая логика для демонстрации
        if request.content_type == ContentType.TEXT:
            return await self._analyze_text(request)
        elif request.content_type == ContentType.IMAGE:
            return await self._analyze_image(request)
        elif request.content_type == ContentType.VIDEO:
            return await self._analyze_video(request)
        else:
            return None
    
    async def _analyze_text(
        self,
        request: ModerationRequest
    ) -> Dict[str, Any]:
        """
        Анализ текстового контента.
        
        Args:
            request: Запрос на модерацию
            
        Returns:
            Dict[str, Any]: Результат анализа
        """
        text = request.content_text or ""
        violations = []
        violation_categories = []
        risk_score = 0.0
        
        # Простые правила для демонстрации
        bad_words = ["spam", "scam", "fake", "hate", "violence"]
        text_lower = text.lower()
        
        for word in bad_words:
            if word in text_lower:
                violations.append({
                    "type": "inappropriate_language",
                    "word": word,
                    "position": text_lower.find(word)
                })
                violation_categories.append("inappropriate_language")
                risk_score += 0.3
        
        # Проверка на спам (повторяющиеся слова)
        words = text.split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_repetition = max(word_counts.values()) if word_counts else 0
            if max_repetition > len(words) * 0.3:
                violations.append({
                    "type": "spam",
                    "repetition_ratio": max_repetition / len(words)
                })
                violation_categories.append("spam")
                risk_score += 0.4
        
        # Определяем результат
        is_approved = risk_score < 0.5
        confidence_score = min(0.9, 0.5 + abs(risk_score - 0.5))
        
        severity_level = None
        if risk_score > 0.8:
            severity_level = SeverityLevel.CRITICAL
        elif risk_score > 0.6:
            severity_level = SeverityLevel.HIGH
        elif risk_score > 0.4:
            severity_level = SeverityLevel.MEDIUM
        elif risk_score > 0.2:
            severity_level = SeverityLevel.LOW
        
        return {
            "is_approved": is_approved,
            "confidence_score": confidence_score,
            "risk_score": risk_score,
            "violations": violations,
            "violation_categories": list(set(violation_categories)),
            "severity_level": severity_level,
            "detailed_analysis": {
                "text_length": len(text),
                "word_count": len(words),
                "language_detected": "en",  # Заглушка
                "sentiment": "negative" if risk_score > 0.5 else "positive"
            }
        }
    
    async def _analyze_image(
        self,
        request: ModerationRequest
    ) -> Dict[str, Any]:
        """
        Анализ изображения.
        
        Args:
            request: Запрос на модерацию
            
        Returns:
            Dict[str, Any]: Результат анализа
        """
        # Заглушка для анализа изображений
        violations = []
        violation_categories = []
        risk_score = 0.1  # По умолчанию низкий риск
        
        # Простая проверка метаданных
        metadata = request.content_metadata or {}
        file_size = metadata.get("file_size", 0)
        
        # Подозрительно большой файл
        if file_size > 10 * 1024 * 1024:  # 10MB
            violations.append({
                "type": "suspicious_file_size",
                "size": file_size
            })
            violation_categories.append("suspicious_content")
            risk_score += 0.2
        
        # Проверка расширения файла
        content_url = request.content_url or ""
        if any(ext in content_url.lower() for ext in ['.exe', '.bat', '.cmd']):
            violations.append({
                "type": "executable_file",
                "extension": content_url.split('.')[-1]
            })
            violation_categories.append("malicious_content")
            risk_score += 0.8
        
        is_approved = risk_score < 0.5
        confidence_score = min(0.9, 0.6 + abs(risk_score - 0.5))
        
        severity_level = None
        if risk_score > 0.8:
            severity_level = SeverityLevel.CRITICAL
        elif risk_score > 0.6:
            severity_level = SeverityLevel.HIGH
        elif risk_score > 0.4:
            severity_level = SeverityLevel.MEDIUM
        elif risk_score > 0.2:
            severity_level = SeverityLevel.LOW
        
        return {
            "is_approved": is_approved,
            "confidence_score": confidence_score,
            "risk_score": risk_score,
            "violations": violations,
            "violation_categories": list(set(violation_categories)),
            "severity_level": severity_level,
            "detailed_analysis": {
                "file_size": file_size,
                "format": metadata.get("format", "unknown"),
                "dimensions": metadata.get("dimensions", "unknown"),
                "has_exif": metadata.get("has_exif", False)
            }
        }
    
    async def _analyze_video(
        self,
        request: ModerationRequest
    ) -> Dict[str, Any]:
        """
        Анализ видео.
        
        Args:
            request: Запрос на модерацию
            
        Returns:
            Dict[str, Any]: Результат анализа
        """
        # Заглушка для анализа видео
        violations = []
        violation_categories = []
        risk_score = 0.2  # По умолчанию низкий риск
        
        metadata = request.content_metadata or {}
        duration = metadata.get("duration", 0)
        file_size = metadata.get("file_size", 0)
        
        # Очень длинное видео
        if duration > 3600:  # 1 час
            violations.append({
                "type": "excessive_duration",
                "duration": duration
            })
            violation_categories.append("policy_violation")
            risk_score += 0.3
        
        # Очень большой файл
        if file_size > 100 * 1024 * 1024:  # 100MB
            violations.append({
                "type": "excessive_file_size",
                "size": file_size
            })
            violation_categories.append("policy_violation")
            risk_score += 0.2
        
        is_approved = risk_score < 0.5
        confidence_score = min(0.9, 0.7 + abs(risk_score - 0.5))
        
        severity_level = None
        if risk_score > 0.8:
            severity_level = SeverityLevel.CRITICAL
        elif risk_score > 0.6:
            severity_level = SeverityLevel.HIGH
        elif risk_score > 0.4:
            severity_level = SeverityLevel.MEDIUM
        elif risk_score > 0.2:
            severity_level = SeverityLevel.LOW
        
        return {
            "is_approved": is_approved,
            "confidence_score": confidence_score,
            "risk_score": risk_score,
            "violations": violations,
            "violation_categories": list(set(violation_categories)),
            "severity_level": severity_level,
            "detailed_analysis": {
                "duration": duration,
                "file_size": file_size,
                "format": metadata.get("format", "unknown"),
                "resolution": metadata.get("resolution", "unknown"),
                "fps": metadata.get("fps", "unknown")
            }
        }
    
    async def get_ai_stats(self) -> Dict[str, Any]:
        """
        Получение статистики AI модерации.
        
        Returns:
            Dict[str, Any]: Статистика AI
        """
        from sqlalchemy import func
        
        # Общее количество AI анализов
        total_analyses_result = await self.db.execute(
            select(func.count(ModerationResult.id))
            .where(ModerationResult.ai_model.isnot(None))
        )
        total_analyses = total_analyses_result.scalar() or 0
        
        # Анализы по типам контента
        analyses_by_type_result = await self.db.execute(
            select(
                ModerationRequest.content_type,
                func.count(ModerationResult.id).label('count')
            )
            .join(ModerationRequest, ModerationResult.request_id == ModerationRequest.id)
            .where(ModerationResult.ai_model.isnot(None))
            .group_by(ModerationRequest.content_type)
        )
        analyses_by_type = {row.content_type.value: row.count for row in analyses_by_type_result}
        
        # Средняя точность
        avg_confidence_result = await self.db.execute(
            select(func.avg(ModerationResult.confidence_score))
            .where(ModerationResult.confidence_score.isnot(None))
        )
        avg_confidence = avg_confidence_result.scalar() or 0.0
        
        # Среднее время обработки
        avg_processing_time_result = await self.db.execute(
            select(func.avg(ModerationResult.processing_time_ms))
            .where(ModerationResult.processing_time_ms.isnot(None))
        )
        avg_processing_time = avg_processing_time_result.scalar() or 0.0
        
        return {
            "total_analyses": total_analyses,
            "analyses_by_type": analyses_by_type,
            "average_confidence": round(avg_confidence, 3),
            "average_processing_time_ms": round(avg_processing_time, 2),
            "available_models": list(self.ai_models.values())
        }
