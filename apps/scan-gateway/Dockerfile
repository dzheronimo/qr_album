FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаём non-root пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Копируем и устанавливаем py-commons
COPY packages/py-commons ./packages/py-commons
RUN pip install --no-cache-dir -e ./packages/py-commons

# Копируем и устанавливаем зависимости
COPY apps/scan-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY apps/scan-gateway/app ./app

# Устанавливаем права на директорию
RUN chown -R appuser:appuser /app

# Переключаемся на non-root пользователя
USER appuser

ENV PYTHONUNBUFFERED=1

# Добавляем health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
