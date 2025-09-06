# 🔍 Детальный анализ бага billing-svc (#audit-006)

**Дата анализа**: 2025-01-27  
**Сервис**: billing-svc  
**Проблема**: Проверка лимитов (незначительная проблема с Pydantic)  

## 📋 Описание проблемы

В TODO.md указано: "Исправить проверку лимитов (незначительная проблема с Pydantic)". После детального анализа кода выявлены несколько потенциальных проблем в методе `check_limits` класса `UsageService`.

## 🔍 Найденные проблемы

### 1. **Проблема с типами данных в арифметических операциях**

**Файл**: `apps/billing-svc/app/services/usage_service.py`  
**Строки**: 259-283  

**Проблема**: В методе `check_limits` есть потенциальная проблема с обработкой `None` значений:

```python
# Строка 260
if albums_count is not None and plan.max_albums is not None:
    current_albums = (current_usage.albums_count if current_usage else 0) + albums_count
    if current_albums > plan.max_albums:
        limits_exceeded.append(f"Превышен лимит альбомов: {current_albums}/{plan.max_albums}")
```

**Анализ**:
- Код проверяет `albums_count is not None`
- Но если `current_usage.albums_count` может быть `None` (что возможно в SQLAlchemy)
- То получится `None + albums_count`, что вызовет `TypeError`

### 2. **Проблема с валидацией Pydantic**

**Файл**: `apps/billing-svc/app/routes/usage.py`  
**Строки**: 36-42  

**Проблема**: В модели `CheckLimitsRequest` есть потенциальная проблема с валидацией:

```python
class CheckLimitsRequest(BaseModel):
    albums_count: Optional[int] = Field(None, ge=0, description="Количество альбомов для проверки")
    pages_count: Optional[int] = Field(None, ge=0, description="Количество страниц для проверки")
    # ... другие поля
```

**Анализ**:
- `Field(None, ge=0)` означает, что если значение не `None`, то оно должно быть >= 0
- Но если передать `None`, валидация пройдёт
- В коде есть проверки `if albums_count is not None`, но нет дополнительной валидации

### 3. **Проблема с обработкой None в SQLAlchemy**

**Файл**: `apps/billing-svc/app/services/usage_service.py`  
**Строки**: 254, 260, 265, 270, 275, 280  

**Проблема**: `current_usage` может быть `None`, но его поля также могут быть `None`:

```python
current_usage = await self.get_current_usage(user_id)

# Строка 260
current_albums = (current_usage.albums_count if current_usage else 0) + albums_count
```

**Анализ**:
- Если `current_usage` существует, но `current_usage.albums_count` равно `None`
- То получится `None + albums_count`, что вызовет `TypeError`

## 🧪 Тестовые сценарии для воспроизведения

### Сценарий 1: None значения в current_usage
```python
# Если в БД current_usage.albums_count = NULL
current_usage.albums_count = None
albums_count = 5

# Результат: None + 5 = TypeError
```

### Сценарий 2: Отрицательные значения (должны блокироваться Pydantic)
```python
# Запрос с отрицательным значением
request = CheckLimitsRequest(albums_count=-1)
# Должно вызвать ValidationError, но может не вызвать
```

### Сценарий 3: Смешанные None и числовые значения
```python
# Запрос с None и числовыми значениями
request = CheckLimitsRequest(
    albums_count=None,
    pages_count=10,
    media_files_count=None
)
# Может вызвать проблемы в логике проверки
```

## 🔧 Предлагаемые исправления

### Исправление 1: Безопасная обработка None значений

```python
async def check_limits(self, ...):
    # ... существующий код ...
    
    current_usage = await self.get_current_usage(user_id)
    
    # Безопасное получение текущих значений
    current_albums_count = (current_usage.albums_count or 0) if current_usage else 0
    current_pages_count = (current_usage.pages_count or 0) if current_usage else 0
    current_media_count = (current_usage.media_files_count or 0) if current_usage else 0
    current_qr_count = (current_usage.qr_codes_count or 0) if current_usage else 0
    current_storage_mb = (current_usage.storage_used_mb or 0) if current_usage else 0
    
    # Проверяем лимиты
    limits_exceeded = []
    
    if albums_count is not None and plan.max_albums is not None:
        total_albums = current_albums_count + albums_count
        if total_albums > plan.max_albums:
            limits_exceeded.append(f"Превышен лимит альбомов: {total_albums}/{plan.max_albums}")
    
    # ... аналогично для других полей ...
```

### Исправление 2: Улучшенная валидация Pydantic

```python
class CheckLimitsRequest(BaseModel):
    """Запрос на проверку лимитов."""
    albums_count: Optional[int] = Field(None, ge=0, description="Количество альбомов для проверки")
    pages_count: Optional[int] = Field(None, ge=0, description="Количество страниц для проверки")
    media_files_count: Optional[int] = Field(None, ge=0, description="Количество медиафайлов для проверки")
    qr_codes_count: Optional[int] = Field(None, ge=0, description="Количество QR кодов для проверки")
    storage_used_mb: Optional[int] = Field(None, ge=0, description="Использованное хранилище в МБ для проверки")
    
    @validator('*', pre=True)
    def validate_positive_values(cls, v):
        """Валидация положительных значений."""
        if v is not None and v < 0:
            raise ValueError('Значение не может быть отрицательным')
        return v
```

### Исправление 3: Добавление unit тестов

```python
import pytest
from app.services.usage_service import UsageService
from app.models.billing import Usage

@pytest.mark.asyncio
async def test_check_limits_with_none_values():
    """Тест проверки лимитов с None значениями."""
    # Создаём мок current_usage с None значениями
    current_usage = Usage(
        albums_count=None,
        pages_count=5,
        media_files_count=None
    )
    
    # Тестируем, что код не падает
    result = await usage_service.check_limits(
        user_id=1,
        albums_count=10,
        pages_count=None,
        media_files_count=20
    )
    
    assert result is not None
    assert 'limits_exceeded' in result

@pytest.mark.asyncio
async def test_check_limits_negative_values():
    """Тест проверки лимитов с отрицательными значениями."""
    with pytest.raises(ValidationError):
        CheckLimitsRequest(albums_count=-1)
```

## 🎯 Приоритет исправления

**Приоритет**: **СРЕДНИЙ**  
**Критичность**: **НИЗКАЯ** (незначительная проблема)  

**Обоснование**:
- Проблема может проявляться только при определённых условиях
- Не влияет на основную функциональность
- Легко исправляется
- Не создаёт уязвимостей безопасности

## 📝 План исправления

1. **Немедленно**: Исправить обработку None значений в методе `check_limits`
2. **В течение недели**: Добавить unit тесты для проверки лимитов
3. **В течение месяца**: Улучшить валидацию Pydantic моделей

## 🔗 Связанные файлы

- `apps/billing-svc/app/services/usage_service.py` - основной файл с проблемой
- `apps/billing-svc/app/routes/usage.py` - Pydantic модели
- `apps/billing-svc/app/models/billing.py` - SQLAlchemy модели
- `TODO.md` - упоминание проблемы

---

**Статус**: ✅ **АНАЛИЗ ЗАВЕРШЁН**  
**Следующий шаг**: Исправление кода и добавление тестов
