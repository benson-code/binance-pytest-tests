"""
安全性測試
"""
import pytest
import time
from utils.binance_client import BinanceClient
from config import Config


@pytest.mark.security
@pytest.mark.p0
class TestAPIAuthentication:
    """API 認證安全測試"""

    def test_missing_signature(self, binance_client_function: BinanceClient, test_symbol: str):
        """TC-S001: 缺少簽名的請求應被拒絕"""
        # 直接發送未簽名的請求
        url = f"{Config.BASE_URL}/api/v3/account"
        params = {'timestamp': int(time.time() * 1000)}

        response = binance_client_function.session.get(url, params=params)

        # 應返回錯誤（401 或 400）
        assert response.status_code in [400, 401], \
            f"缺少簽名應返回 400/401，實際: {response.status_code}"

        error_data = response.json()
        assert 'code' in error_data
        assert 'msg' in error_data

    def test_invalid_signature(self, binance_client_function: BinanceClient):
        """TC-S002: 錯誤的簽名應被拒絕"""
        url = f"{Config.BASE_URL}/api/v3/account"
        params = {
            'timestamp': int(time.time() * 1000),
            'signature': 'invalid_signature_12345'
        }

        response = binance_client_function.session.get(url, params=params)

        assert response.status_code == 401, "錯誤簽名應返回 401"
        error_data = response.json()
        assert error_data['code'] == -1022, "應返回簽名錯誤代碼"

    def test_invalid_api_key(self):
        """TC-S003: 無效的 API Key 應被拒絕"""
        # 使用假的 API Key
        fake_client = BinanceClient(
            api_key='fake_api_key_12345',
            secret_key='fake_secret_key_12345'
        )

        response = fake_client.get_account_info()

        assert response.status_code in [401, 403], "無效 API Key 應返回 401/403"
        error_data = response.json()
        assert error_data['code'] == -2015, "應返回 API Key 錯誤代碼"

        fake_client.close()

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_expired_timestamp(self, binance_client: BinanceClient):
        """TC-S004: 過期的時間戳應被拒絕"""
        url = f"{Config.BASE_URL}/api/v3/account"

        # 使用 5 分鐘前的時間戳
        old_timestamp = int(time.time() * 1000) - 300000
        params = {
            'timestamp': old_timestamp
        }

        # 手動生成簽名
        import hmac
        import hashlib
        from urllib.parse import urlencode

        query_string = urlencode(params)
        signature = hmac.new(
            Config.SECRET_KEY.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        params['signature'] = signature

        response = binance_client.session.get(url, params=params)

        assert response.status_code == 400, "過期時間戳應返回 400"
        error_data = response.json()
        assert error_data['code'] == -1021, "應返回時間戳錯誤代碼"


@pytest.mark.security
@pytest.mark.p1
class TestInputValidation:
    """輸入驗證安全測試"""

    def test_sql_injection_in_symbol(self, binance_client: BinanceClient):
        """TC-S005: SQL 注入測試 - symbol 參數"""
        malicious_symbol = "BTCUSDT' OR '1'='1"

        response = binance_client.get_order_book(symbol=malicious_symbol, limit=5)

        # 應返回參數錯誤，而非 SQL 錯誤
        assert response.status_code == 400, "應拒絕惡意 SQL 輸入"
        error_data = response.json()
        # 確保錯誤訊息不包含 SQL 相關資訊
        assert 'SQL' not in error_data.get('msg', '').upper()

    def test_xss_injection_attempt(self, binance_client: BinanceClient):
        """TC-S006: XSS 攻擊測試"""
        xss_payload = "<script>alert('XSS')</script>"

        response = binance_client.get_order_book(symbol=xss_payload, limit=5)

        assert response.status_code == 400, "應拒絕 XSS payload"

        # 檢查響應是否正確轉義
        response_text = response.text
        # 腳本標籤不應直接出現在響應中
        assert '<script>' not in response_text.lower()

    def test_extremely_large_limit(self, binance_client: BinanceClient, test_symbol: str):
        """TC-S007: 測試超大 limit 參數"""
        response = binance_client.get_klines(
            symbol=test_symbol,
            interval='1h',
            limit=100000  # 遠超過合理範圍
        )

        # 應限制到最大值或返回錯誤
        if response.status_code == 200:
            data = response.json()
            # 應自動限制到最大值
            assert len(data) <= 1000, "應限制返回數量"
        else:
            # 或返回參數錯誤
            assert response.status_code == 400


@pytest.mark.security
@pytest.mark.p0
class TestHTTPSSecurity:
    """HTTPS 安全性測試"""

    def test_https_enforced(self):
        """TC-S008: 驗證強制使用 HTTPS"""
        import ssl
        import socket

        hostname = "testnet.binance.vision"
        port = 443

        context = ssl.create_default_context()

        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # 獲取 SSL 憑證資訊
                cert = ssock.getpeercert()

                # 驗證憑證存在
                assert cert is not None, "應有有效的 SSL 憑證"

                # 驗證 TLS 版本
                tls_version = ssock.version()
                assert tls_version in ['TLSv1.2', 'TLSv1.3'], \
                    f"應使用 TLS 1.2 或更高版本，實際: {tls_version}"
