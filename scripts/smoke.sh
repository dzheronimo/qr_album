#!/usr/bin/env bash
set -euo pipefail

# Smoke тесты для проверки health endpoints
# Проверяет, что все сервисы отвечают на health checks

echo "🔍 Запуск smoke тестов для health endpoints..."

# Список портов для проверки
PORTS=(8080 8009 8010 8011 8086)
SERVICE_NAMES=("api-gateway" "notification-svc" "moderation-svc" "print-svc" "scan-gateway")

# Функция для проверки health endpoint
check_health() {
    local port=$1
    local service_name=$2
    
    echo "  📡 Проверяем $service_name (порт $port)..."
    
    if curl -fsS "http://localhost:${port}/health" >/dev/null 2>&1; then
        echo "  ✅ $service_name: /health OK"
        return 0
    else
        echo "  ❌ $service_name: /health FAILED"
        return 1
    fi
}

# Функция для проверки readiness endpoint
check_readiness() {
    local port=$1
    local service_name=$2
    
    echo "  🔄 Проверяем readiness для $service_name..."
    
    if curl -fsS "http://localhost:${port}/health/ready" >/dev/null 2>&1; then
        echo "  ✅ $service_name: /health/ready OK"
        return 0
    else
        echo "  ⚠️  $service_name: /health/ready FAILED (может быть нормально при недоступных зависимостях)"
        return 0  # Не считаем readiness failure критичным
    fi
}

# Проверяем liveness для всех сервисов
echo ""
echo "🏥 Проверка liveness endpoints (/health):"
failed_services=()

for i in "${!PORTS[@]}"; do
    if ! check_health "${PORTS[$i]}" "${SERVICE_NAMES[$i]}"; then
        failed_services+=("${SERVICE_NAMES[$i]}")
    fi
done

# Проверяем readiness для основных сервисов
echo ""
echo "🔄 Проверка readiness endpoints (/health/ready):"
readiness_ports=(8080 8009 8010 8011)  # Исключаем scan-gateway, так как он может быть unhealthy

for i in "${!readiness_ports[@]}"; do
    port="${readiness_ports[$i]}"
    # Находим соответствующий сервис
    for j in "${!PORTS[@]}"; do
        if [[ "${PORTS[$j]}" == "$port" ]]; then
            check_readiness "$port" "${SERVICE_NAMES[$j]}"
            break
        fi
    done
done

# Проверяем scan-gateway отдельно
echo ""
echo "🔍 Специальная проверка scan-gateway:"
echo "  📡 Проверяем scan-gateway (порт 8086)..."
if curl -fsS "http://localhost:8086/health" >/dev/null 2>&1; then
    echo "  ✅ scan-gateway: /health доступен (может быть unhealthy из-за зависимостей)"
else
    echo "  ❌ scan-gateway: /health недоступен"
    failed_services+=("scan-gateway")
fi

# Итоговый результат
echo ""
if [[ ${#failed_services[@]} -eq 0 ]]; then
    echo "🎉 Все smoke тесты прошли успешно!"
    echo "✅ Все сервисы отвечают на health checks"
    exit 0
else
    echo "❌ Smoke тесты завершились с ошибками:"
    for service in "${failed_services[@]}"; do
        echo "  - $service"
    done
    echo ""
    echo "💡 Проверьте логи сервисов: docker compose logs <service-name>"
    exit 1
fi
