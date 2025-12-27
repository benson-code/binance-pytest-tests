"""
性能測試
"""
import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.binance_client import BinanceClient


@pytest.mark.performance
@pytest.mark.p1
class TestResponseTime:
    """響應時間測試"""

    def test_ping_response_time(self, binance_client: BinanceClient):
        """TC-P001: Ping 端點響應時間"""
        response_times = []

        # 測試 10 次
        for _ in range(10):
            start = time.time()
            response = binance_client.ping()
            elapsed = time.time() - start

            assert response.status_code == 200
            response_times.append(elapsed)

        # 統計分析
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        print(f"\n響應時間統計:")
        print(f"  平均: {avg_time:.3f}s")
        print(f"  最小: {min_time:.3f}s")
        print(f"  最大: {max_time:.3f}s")

        # 斷言平均響應時間 < 0.5 秒
        assert avg_time < 0.5, f"平均響應時間應小於 0.5s，實際: {avg_time:.3f}s"

    def test_market_data_response_time(self, binance_client: BinanceClient, test_symbol: str):
        """TC-P002: 市場數據查詢響應時間"""
        start = time.time()
        response = binance_client.get_order_book(symbol=test_symbol, limit=100)
        elapsed = time.time() - start

        assert response.status_code == 200
        print(f"\n深度查詢響應時間: {elapsed:.3f}s")

        # 斷言響應時間 < 1 秒
        assert elapsed < 1.0, f"響應時間應小於 1s，實際: {elapsed:.3f}s"

    @pytest.mark.slow
    def test_large_data_query_performance(self, binance_client: BinanceClient, test_symbol: str):
        """TC-P003: 大量數據查詢性能"""
        start = time.time()
        response = binance_client.get_klines(
            symbol=test_symbol,
            interval='1h',
            limit=1000
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        data = response.json()

        print(f"\n查詢 {len(data)} 根 K 線耗時: {elapsed:.3f}s")

        # 斷言響應時間 < 2 秒
        assert elapsed < 2.0, f"大量數據查詢應小於 2s，實際: {elapsed:.3f}s"


@pytest.mark.performance
@pytest.mark.p1
class TestConcurrency:
    """併發測試"""

    def test_concurrent_requests(self, test_symbol: str):
        """TC-P004: 併發請求測試"""
        num_requests = 50

        def make_request(i):
            client = BinanceClient()
            start = time.time()
            response = client.get_server_time()
            elapsed = time.time() - start
            client.close()
            return i, response.status_code, elapsed

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [f.result() for f in as_completed(futures)]

        total_time = time.time() - start_time

        # 統計
        success_count = sum(1 for _, status, _ in results if status == 200)
        avg_response_time = statistics.mean([elapsed for _, _, elapsed in results])

        print(f"\n併發測試結果:")
        print(f"  總請求數: {num_requests}")
        print(f"  成功數: {success_count}")
        print(f"  總耗時: {total_time:.2f}s")
        print(f"  平均響應時間: {avg_response_time:.3f}s")

        # 斷言
        assert success_count == num_requests, f"所有請求都應成功，成功率: {success_count}/{num_requests}"
        assert total_time < 10, f"併發請求總時間應小於 10s，實際: {total_time:.2f}s"

    @pytest.mark.slow
    def test_sustained_load(self, binance_client: BinanceClient, test_symbol: str):
        """TC-P005: 持續負載測試"""
        duration = 30  # 測試 30 秒
        request_count = 0
        error_count = 0
        start_time = time.time()

        print(f"\n持續負載測試 ({duration} 秒)...")

        while time.time() - start_time < duration:
            try:
                response = binance_client.ping()
                if response.status_code == 200:
                    request_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1

            time.sleep(0.1)  # 100ms 間隔

        elapsed = time.time() - start_time
        requests_per_second = request_count / elapsed

        print(f"\n持續負載測試結果:")
        print(f"  總請求數: {request_count}")
        print(f"  錯誤數: {error_count}")
        print(f"  持續時間: {elapsed:.2f}s")
        print(f"  平均 RPS: {requests_per_second:.2f}")

        # 斷言錯誤率 < 1%
        error_rate = error_count / (request_count + error_count) if request_count > 0 else 1
        assert error_rate < 0.01, f"錯誤率應小於 1%，實際: {error_rate*100:.2f}%"


@pytest.mark.performance
@pytest.mark.p2
@pytest.mark.slow
class TestRateLimit:
    """速率限制測試"""

    def test_rate_limit_detection(self, binance_client: BinanceClient):
        """TC-P006: 速率限制測試（謹慎執行）"""
        # 注意：此測試會嘗試觸發速率限制，執行需謹慎

        print("\n測試速率限制（發送快速連續請求）...")
        request_count = 0
        rate_limit_hit = False

        for i in range(1500):  # 嘗試發送大量請求
            response = binance_client.get_server_time()

            if response.status_code == 429:
                print(f"在第 {i+1} 次請求時觸發速率限制")
                rate_limit_hit = True

                # 檢查響應頭
                if 'Retry-After' in response.headers:
                    print(f"Retry-After: {response.headers['Retry-After']}")

                break

            request_count += 1

            if i % 100 == 0:
                print(f"已完成 {i} 次請求")
                time.sleep(0.1)  # 稍微降低速度

        print(f"\n總共發送 {request_count} 次請求")

        if rate_limit_hit:
            print("成功檢測到速率限制機制")
        else:
            print("未觸發速率限制（可能測試環境限制較寬鬆）")


@pytest.mark.performance
@pytest.mark.p2
class TestDataIntegrity:
    """數據完整性與一致性測試"""

    def test_repeated_queries_consistency(
        self, binance_client: BinanceClient, test_symbol: str
    ):
        """TC-P007: 重複查詢數據一致性"""
        # 連續查詢 5 次 24hr ticker
        results = []

        for _ in range(5):
            response = binance_client.get_24hr_ticker(symbol=test_symbol)
            assert response.status_code == 200
            results.append(response.json())
            time.sleep(0.5)

        # 驗證數據結構一致
        for result in results:
            assert 'symbol' in result
            assert 'lastPrice' in result
            assert result['symbol'] == test_symbol

        print(f"\n5 次查詢結果結構一致")
