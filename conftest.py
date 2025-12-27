"""
Pytest 配置和 Fixtures
"""
import pytest
import logging
from typing import Generator

from utils.binance_client import BinanceClient
from config import Config

# 配置日誌
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)


@pytest.fixture(scope="session")
def binance_client() -> Generator[BinanceClient, None, None]:
    """
    Session 級別的 Binance 客戶端
    整個測試會話共用一個客戶端實例
    """
    client = BinanceClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def binance_client_function() -> Generator[BinanceClient, None, None]:
    """
    Function 級別的 Binance 客戶端
    每個測試函數都會創建新的客戶端實例
    """
    client = BinanceClient()
    yield client
    client.close()


@pytest.fixture(scope="session")
def test_symbol():
    """測試用交易對"""
    return Config.DEFAULT_SYMBOL


@pytest.fixture(scope="session")
def test_symbols():
    """測試用交易對列表"""
    return Config.TEST_SYMBOLS


@pytest.fixture
def order_params():
    """測試訂單參數"""
    return {
        'symbol': Config.DEFAULT_SYMBOL,
        'side': 'BUY',
        'order_type': 'LIMIT',
        'quantity': Config.TEST_ORDER_QUANTITY,
        'price': Config.TEST_ORDER_PRICE,
        'time_in_force': 'GTC'
    }


@pytest.fixture
def market_order_params():
    """市價單參數"""
    return {
        'symbol': Config.DEFAULT_SYMBOL,
        'side': 'BUY',
        'order_type': 'MARKET',
        'quantity': 0.0001  # 極小數量避免消耗太多測試資金
    }


# ==================== Hooks ====================

def pytest_configure(config):
    """Pytest 配置 hook"""
    # 註冊自定義標記
    config.addinivalue_line(
        "markers", "smoke: 冒煙測試"
    )


def pytest_collection_modifyitems(config, items):
    """修改測試項目的 hook"""
    # 為沒有標記的測試添加默認標記
    for item in items:
        if "test_security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        if "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)


def pytest_html_report_title(report):
    """自定義 HTML 報告標題"""
    report.title = "Binance Testnet API 測試報告"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    測試執行報告 hook
    用於在測試失敗時添加額外資訊
    """
    outcome = yield
    report = outcome.get_result()

    # 為 HTML 報告添加額外資訊
    if report.when == "call":
        # 添加測試描述
        if hasattr(item, 'obj'):
            doc = item.obj.__doc__
            if doc:
                report.description = doc.strip()

        # 測試失敗時的處理
        if report.failed:
            logging.error(f"Test failed: {item.nodeid}")
