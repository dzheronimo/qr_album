# Smoke тесты для проверки health endpoints
# Проверяет, что все сервисы отвечают на health checks

Write-Host "🔍 Запуск smoke тестов для health endpoints..." -ForegroundColor Cyan

# Список портов и сервисов для проверки
$services = @(
    @{Port=8080; Name="api-gateway"},
    @{Port=8009; Name="notification-svc"},
    @{Port=8010; Name="moderation-svc"},
    @{Port=8011; Name="print-svc"},
    @{Port=8086; Name="scan-gateway"}
)

# Функция для проверки health endpoint
function Test-HealthEndpoint {
    param(
        [int]$Port,
        [string]$ServiceName
    )
    
    Write-Host "  📡 Проверяем $ServiceName (порт $Port)..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $ServiceName`: /health OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ $ServiceName`: /health FAILED (Status: $($response.StatusCode))" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  ❌ $ServiceName`: /health FAILED ($($_.Exception.Message))" -ForegroundColor Red
        return $false
    }
}

# Функция для проверки readiness endpoint
function Test-ReadinessEndpoint {
    param(
        [int]$Port,
        [string]$ServiceName
    )
    
    Write-Host "  🔄 Проверяем readiness для $ServiceName..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health/ready" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $ServiceName`: /health/ready OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ⚠️  $ServiceName`: /health/ready FAILED (Status: $($response.StatusCode))" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "  ⚠️  $ServiceName`: /health/ready FAILED ($($_.Exception.Message))" -ForegroundColor Yellow
        return $false
    }
}

# Проверяем liveness для всех сервисов
Write-Host ""
Write-Host "🏥 Проверка liveness endpoints (/health):" -ForegroundColor Cyan
$failedServices = @()

foreach ($service in $services) {
    if (-not (Test-HealthEndpoint -Port $service.Port -ServiceName $service.Name)) {
        $failedServices += $service.Name
    }
}

# Проверяем readiness для основных сервисов (исключаем scan-gateway)
Write-Host ""
Write-Host "🔄 Проверка readiness endpoints (/health/ready):" -ForegroundColor Cyan
$readinessServices = $services | Where-Object { $_.Name -ne "scan-gateway" }

foreach ($service in $readinessServices) {
    Test-ReadinessEndpoint -Port $service.Port -ServiceName $service.Name
}

# Специальная проверка scan-gateway
Write-Host ""
Write-Host "🔍 Специальная проверка scan-gateway:" -ForegroundColor Cyan
$scanGateway = $services | Where-Object { $_.Name -eq "scan-gateway" }
if ($scanGateway) {
    Write-Host "  📡 Проверяем scan-gateway (порт $($scanGateway.Port))..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($scanGateway.Port)/health" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ scan-gateway: /health доступен (может быть unhealthy из-за зависимостей)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ scan-gateway: /health недоступен (Status: $($response.StatusCode))" -ForegroundColor Red
            $failedServices += "scan-gateway"
        }
    } catch {
        Write-Host "  ❌ scan-gateway: /health недоступен ($($_.Exception.Message))" -ForegroundColor Red
        $failedServices += "scan-gateway"
    }
}

# Итоговый результат
Write-Host ""
if ($failedServices.Count -eq 0) {
    Write-Host "🎉 Все smoke тесты прошли успешно!" -ForegroundColor Green
    Write-Host "✅ Все сервисы отвечают на health checks" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Smoke тесты завершились с ошибками:" -ForegroundColor Red
    foreach ($service in $failedServices) {
        Write-Host "  - $service" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "💡 Проверьте логи сервисов: docker compose logs <service-name>" -ForegroundColor Yellow
    exit 1
}
