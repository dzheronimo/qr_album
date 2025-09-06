#!/usr/bin/env python3
"""
Скрипт для нагрузочного тестирования QR-Albums сервисов.
"""

import asyncio
import time
import statistics
import json
from typing import List, Dict, Any
import httpx
from datetime import datetime


class LoadTester:
    """Класс для проведения нагрузочного тестирования."""
    
    def __init__(self):
        self.results = []
        self.errors = []
    
    async def test_endpoint(
        self, 
        url: str, 
        method: str = "GET", 
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None,
        concurrent_requests: int = 10,
        total_requests: int = 100
    ) -> Dict[str, Any]:
        """
        Тестирует эндпоинт с заданными параметрами.
        
        Args:
            url: URL для тестирования
            method: HTTP метод
            headers: HTTP заголовки
            data: Данные для POST/PUT запросов
            concurrent_requests: Количество одновременных запросов
            total_requests: Общее количество запросов
            
        Returns:
            Словарь с результатами тестирования
        """
        print(f"🧪 Тестируем {method} {url}")
        print(f"   Запросов: {total_requests}, одновременных: {concurrent_requests}")
        
        start_time = time.time()
        response_times = []
        status_codes = {}
        errors = []
        
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def make_request():
            async with semaphore:
                try:
                    request_start = time.time()
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        if method == "GET":
                            response = await client.get(url, headers=headers)
                        elif method == "POST":
                            response = await client.post(url, headers=headers, json=data)
                        else:
                            response = await client.request(method, url, headers=headers, json=data)
                    
                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    
                    status_code = response.status_code
                    status_codes[status_code] = status_codes.get(status_code, 0) + 1
                    
                except Exception as e:
                    errors.append(str(e))
        
        # Создаем задачи для всех запросов
        tasks = [make_request() for _ in range(total_requests)]
        
        # Выполняем все запросы
        await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Вычисляем статистику
        if response_times:
            p50 = statistics.median(response_times)
            p95 = statistics.quantiles(response_times, n=20)[18]  # 95-й процентиль
            p99 = statistics.quantiles(response_times, n=100)[98]  # 99-й процентиль
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
        else:
            p50 = p95 = p99 = avg_time = min_time = max_time = 0
        
        # Вычисляем RPS
        rps = total_requests / total_time if total_time > 0 else 0
        
        # Подсчитываем ошибки
        error_rate = len(errors) / total_requests * 100 if total_requests > 0 else 0
        
        result = {
            "url": url,
            "method": method,
            "total_requests": total_requests,
            "concurrent_requests": concurrent_requests,
            "total_time": total_time,
            "rps": rps,
            "response_times": {
                "min": min_time,
                "max": max_time,
                "avg": avg_time,
                "p50": p50,
                "p95": p95,
                "p99": p99
            },
            "status_codes": status_codes,
            "error_rate": error_rate,
            "errors": errors[:10],  # Первые 10 ошибок
            "timestamp": datetime.now().isoformat()
        }
        
        self.results.append(result)
        return result
    
    def print_summary(self, result: Dict[str, Any]):
        """Выводит краткую сводку результатов."""
        print(f"   ✅ RPS: {result['rps']:.2f}")
        print(f"   ⏱️  Время ответа: avg={result['response_times']['avg']:.3f}s, p95={result['response_times']['p95']:.3f}s, p99={result['response_times']['p99']:.3f}s")
        print(f"   📊 Статус коды: {result['status_codes']}")
        if result['error_rate'] > 0:
            print(f"   ❌ Ошибки: {result['error_rate']:.1f}% ({len(result['errors'])} ошибок)")
        print()
    
    def save_results(self, filename: str):
        """Сохраняет результаты в JSON файл."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"📁 Результаты сохранены в {filename}")


async def main():
    """Основная функция для проведения нагрузочного тестирования."""
    print("🚀 Начинаем нагрузочное тестирование QR-Albums")
    print("=" * 60)
    
    tester = LoadTester()
    
    # Тестируем основные эндпоинты
    endpoints = [
        # API Gateway
        ("http://localhost:8080/healthz", "GET"),
        ("http://localhost:8080/docs", "GET"),
        
        # Scan Gateway
        ("http://localhost:8086/healthz", "GET"),
        
        # Микросервисы
        ("http://localhost:8001/health", "GET"),  # auth-svc
        ("http://localhost:8002/health", "GET"),  # album-svc
        ("http://localhost:8003/health", "GET"),  # media-svc
        ("http://localhost:8005/health", "GET"),  # qr-svc
        ("http://localhost:8006/health", "GET"),  # user-profile-svc
        ("http://localhost:8007/health", "GET"),  # analytics-svc
        ("http://localhost:8008/health", "GET"),  # billing-svc
        ("http://localhost:8009/health", "GET"),  # notification-svc
        ("http://localhost:8010/health", "GET"),  # moderation-svc
        ("http://localhost:8011/health", "GET"),  # print-svc
    ]
    
    # Тестируем каждый эндпоинт
    for url, method in endpoints:
        try:
            result = await tester.test_endpoint(
                url=url,
                method=method,
                concurrent_requests=5,
                total_requests=50
            )
            tester.print_summary(result)
        except Exception as e:
            print(f"❌ Ошибка при тестировании {url}: {e}")
            print()
    
    # Специальные тесты для критических эндпоинтов
    print("🔥 Тестируем критические эндпоинты с высокой нагрузкой")
    print("-" * 60)
    
    # API Gateway health check с высокой нагрузкой
    try:
        result = await tester.test_endpoint(
            url="http://localhost:8080/healthz",
            method="GET",
            concurrent_requests=20,
            total_requests=200
        )
        print("API Gateway Health Check (высокая нагрузка):")
        tester.print_summary(result)
    except Exception as e:
        print(f"❌ Ошибка при высоконагруженном тестировании API Gateway: {e}")
    
    # Scan Gateway с высокой нагрузкой
    try:
        result = await tester.test_endpoint(
            url="http://localhost:8086/healthz",
            method="GET",
            concurrent_requests=20,
            total_requests=200
        )
        print("Scan Gateway Health Check (высокая нагрузка):")
        tester.print_summary(result)
    except Exception as e:
        print(f"❌ Ошибка при высоконагруженном тестировании Scan Gateway: {e}")
    
    # Сохраняем результаты
    tester.save_results("audit/reports/load/load-test-results.json")
    
    # Выводим общую сводку
    print("📊 ОБЩАЯ СВОДКА")
    print("=" * 60)
    
    total_tests = len(tester.results)
    successful_tests = len([r for r in tester.results if r['error_rate'] == 0])
    failed_tests = total_tests - successful_tests
    
    print(f"Всего тестов: {total_tests}")
    print(f"Успешных: {successful_tests}")
    print(f"С ошибками: {failed_tests}")
    
    if tester.results:
        avg_rps = statistics.mean([r['rps'] for r in tester.results])
        avg_response_time = statistics.mean([r['response_times']['avg'] for r in tester.results])
        max_p95 = max([r['response_times']['p95'] for r in tester.results])
        
        print(f"Средний RPS: {avg_rps:.2f}")
        print(f"Среднее время ответа: {avg_response_time:.3f}s")
        print(f"Максимальный p95: {max_p95:.3f}s")
    
    print("\n🎯 Рекомендации:")
    if failed_tests > 0:
        print("❌ Обнаружены проблемы с производительностью")
        print("   - Проверьте логи сервисов")
        print("   - Увеличьте ресурсы контейнеров")
        print("   - Оптимизируйте запросы к БД")
    else:
        print("✅ Все тесты прошли успешно")
        print("   - Система готова к нагрузке")
        print("   - Рекомендуется мониторинг в продакшене")


if __name__ == "__main__":
    asyncio.run(main())
