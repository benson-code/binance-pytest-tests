"""
配置文件 - 幣安測試網 API 測試
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """測試配置類"""

    # API 配置
    BASE_URL = os.getenv('BINANCE_BASE_URL', 'https://testnet.binance.vision')
    API_KEY = os.getenv('BINANCE_API_KEY', '')
    SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', '')

    # WebSocket 配置
    WS_URL = os.getenv('BINANCE_WS_URL', 'wss://testnet.binance.vision/ws')

    # 請求配置
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

    # API 端點
    API_V3 = f"{BASE_URL}/api/v3"

    # 常用交易對
    DEFAULT_SYMBOL = "BTCUSDT"
    TEST_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

    # 測試數據
    TEST_ORDER_QUANTITY = 0.001  # BTC
    TEST_ORDER_PRICE = 20000     # USDT

    # 日誌配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate(cls):
        """驗證配置是否完整"""
        errors = []

        if not cls.API_KEY:
            errors.append("BINANCE_API_KEY 未設定")

        if not cls.SECRET_KEY:
            errors.append("BINANCE_SECRET_KEY 未設定")

        if errors:
            raise ValueError(f"配置錯誤: {', '.join(errors)}")

        return True

    @classmethod
    def is_configured(cls):
        """檢查是否已配置（不拋出異常）"""
        return bool(cls.API_KEY and cls.SECRET_KEY)


# 測試時驗證配置（只在需要 API Key 的測試時）
def require_api_credentials():
    """裝飾器：要求 API 憑證"""
    import pytest

    def decorator(func):
        if not Config.is_configured():
            return pytest.mark.skip(reason="需要設定 API 憑證")(func)
        return func

    return decorator
