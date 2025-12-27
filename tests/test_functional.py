"""
功能性測試 - 基礎 API 功能
"""
import pytest
from utils.binance_client import BinanceClient


@pytest.mark.functional
@pytest.mark.smoke
@pytest.mark.p0
class TestBasicFunctionality:
    """基礎功能測試類"""

    def test_ping_connection(self, binance_client: BinanceClient):
        """TC-F001: 測試 API 連線 - Ping"""
        response = binance_client.ping()

        assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
        assert response.json() == {}, "Ping 應返回空 JSON 物件"

    def test_get_server_time(self, binance_client: BinanceClient):
        """TC-F002: 獲取伺服器時間"""
        response = binance_client.get_server_time()

        assert response.status_code == 200
        data = response.json()
        assert 'serverTime' in data, "響應應包含 serverTime"
        assert isinstance(data['serverTime'], int), "serverTime 應為整數"
        assert data['serverTime'] > 0, "serverTime 應大於 0"

    def test_get_exchange_info(self, binance_client: BinanceClient):
        """TC-F003: 獲取交易所資訊"""
        response = binance_client.get_exchange_info()

        assert response.status_code == 200
        data = response.json()
        assert 'symbols' in data, "響應應包含 symbols 陣列"
        assert len(data['symbols']) > 0, "交易對列表不應為空"

    def test_get_exchange_info_specific_symbol(
        self, binance_client: BinanceClient, test_symbol: str
    ):
        """TC-F004: 獲取特定交易對資訊"""
        response = binance_client.get_exchange_info(symbol=test_symbol)

        assert response.status_code == 200
        data = response.json()
        assert 'symbols' in data
        symbols = data['symbols']
        assert len(symbols) >= 1, f"應包含 {test_symbol} 資訊"

        # 驗證交易對資料結構
        symbol_info = symbols[0]
        assert symbol_info['symbol'] == test_symbol
        assert 'baseAsset' in symbol_info
        assert 'quoteAsset' in symbol_info
        assert 'filters' in symbol_info

    def test_get_order_book(self, binance_client: BinanceClient, test_symbol: str):
        """TC-F005: 獲取深度資訊"""
        limit = 5
        response = binance_client.get_order_book(symbol=test_symbol, limit=limit)

        assert response.status_code == 200
        data = response.json()

        # 驗證結構
        assert 'bids' in data, "響應應包含 bids"
        assert 'asks' in data, "響應應包含 asks"

        # 驗證數量
        assert len(data['bids']) <= limit, f"bids 數量應不超過 {limit}"
        assert len(data['asks']) <= limit, f"asks 數量應不超過 {limit}"

        # 驗證 bids 排序（價格遞減）
        if len(data['bids']) > 1:
            for i in range(len(data['bids']) - 1):
                assert float(data['bids'][i][0]) > float(data['bids'][i + 1][0]), \
                    "Bids 應按價格遞減排序"

        # 驗證 asks 排序（價格遞增）
        if len(data['asks']) > 1:
            for i in range(len(data['asks']) - 1):
                assert float(data['asks'][i][0]) < float(data['asks'][i + 1][0]), \
                    "Asks 應按價格遞增排序"

    def test_get_recent_trades(self, binance_client: BinanceClient, test_symbol: str):
        """TC-F006: 獲取最近交易"""
        limit = 10
        response = binance_client.get_recent_trades(symbol=test_symbol, limit=limit)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list), "響應應為陣列"
        assert len(data) <= limit, f"交易數量應不超過 {limit}"

        # 驗證交易資料結構
        if len(data) > 0:
            trade = data[0]
            required_fields = ['id', 'price', 'qty', 'time']
            for field in required_fields:
                assert field in trade, f"交易記錄應包含 {field}"

    def test_get_klines(self, binance_client: BinanceClient, test_symbol: str):
        """TC-F007: 獲取 K 線數據"""
        limit = 10
        interval = '1h'
        response = binance_client.get_klines(
            symbol=test_symbol,
            interval=interval,
            limit=limit
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list), "響應應為陣列"
        assert len(data) <= limit, f"K 線數量應不超過 {limit}"

        # 驗證 K 線資料結構（12 個欄位）
        if len(data) > 0:
            kline = data[0]
            assert len(kline) == 12, "每根 K 線應包含 12 個欄位"
            # 驗證開盤時間
            assert isinstance(kline[0], int), "開盤時間應為整數"

    def test_get_24hr_ticker(self, binance_client: BinanceClient, test_symbol: str):
        """TC-F008: 獲取 24 小時價格統計"""
        response = binance_client.get_24hr_ticker(symbol=test_symbol)

        assert response.status_code == 200
        data = response.json()

        # 驗證必要欄位
        required_fields = [
            'symbol', 'priceChange', 'priceChangePercent',
            'lastPrice', 'volume', 'quoteVolume'
        ]
        for field in required_fields:
            assert field in data, f"24hr ticker 應包含 {field}"

        assert data['symbol'] == test_symbol


@pytest.mark.functional
@pytest.mark.p1
class TestMultipleSymbols:
    """多交易對測試"""

    def test_multiple_symbols_order_book(
        self, binance_client: BinanceClient, test_symbols: list
    ):
        """TC-F009: 測試多個交易對的深度查詢"""
        for symbol in test_symbols:
            response = binance_client.get_order_book(symbol=symbol, limit=5)
            assert response.status_code == 200, f"{symbol} 深度查詢失敗"

            data = response.json()
            assert 'bids' in data
            assert 'asks' in data

    def test_multiple_symbols_klines(
        self, binance_client: BinanceClient, test_symbols: list
    ):
        """TC-F010: 測試多個交易對的 K 線查詢"""
        for symbol in test_symbols:
            response = binance_client.get_klines(
                symbol=symbol,
                interval='1h',
                limit=5
            )
            assert response.status_code == 200, f"{symbol} K 線查詢失敗"

            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
