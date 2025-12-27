"""
Binance API 客戶端封裝
提供簽名、請求等功能
"""
import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests
import logging
from typing import Dict, Optional, Any

from config import Config

logger = logging.getLogger(__name__)


class BinanceClient:
    """幣安 API 客戶端"""

    def __init__(self, api_key: str = None, secret_key: str = None):
        """
        初始化客戶端

        Args:
            api_key: API 密鑰
            secret_key: Secret 密鑰
        """
        self.api_key = api_key or Config.API_KEY
        self.secret_key = secret_key or Config.SECRET_KEY
        self.base_url = Config.BASE_URL
        self.timeout = Config.REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key
        })

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        生成 HMAC SHA256 簽名

        Args:
            params: 請求參數

        Returns:
            簽名字串
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _get_timestamp(self) -> int:
        """獲取當前時間戳（毫秒）"""
        return int(time.time() * 1000)

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> requests.Response:
        """
        發送 HTTP 請求

        Args:
            method: HTTP 方法 (GET, POST, DELETE)
            endpoint: API 端點
            params: 請求參數
            signed: 是否需要簽名

        Returns:
            Response 對象
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}

        if signed:
            params['timestamp'] = self._get_timestamp()
            params['signature'] = self._generate_signature(params)

        logger.debug(f"{method} {url} - Params: {params}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                timeout=self.timeout
            )
            logger.debug(f"Response: {response.status_code} - {response.text[:200]}")
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    # ==================== 公開 API (無需認證) ====================

    def ping(self) -> requests.Response:
        """測試連線"""
        return self._request('GET', '/api/v3/ping')

    def get_server_time(self) -> requests.Response:
        """獲取伺服器時間"""
        return self._request('GET', '/api/v3/time')

    def get_exchange_info(self, symbol: str = None) -> requests.Response:
        """
        獲取交易所資訊

        Args:
            symbol: 交易對（可選）
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._request('GET', '/api/v3/exchangeInfo', params=params)

    def get_order_book(self, symbol: str, limit: int = 100) -> requests.Response:
        """
        獲取深度資訊

        Args:
            symbol: 交易對
            limit: 返回數量 (預設 100)
        """
        params = {'symbol': symbol, 'limit': limit}
        return self._request('GET', '/api/v3/depth', params=params)

    def get_recent_trades(self, symbol: str, limit: int = 500) -> requests.Response:
        """
        獲取最近交易

        Args:
            symbol: 交易對
            limit: 返回數量 (預設 500，最大 1000)
        """
        params = {'symbol': symbol, 'limit': limit}
        return self._request('GET', '/api/v3/trades', params=params)

    def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500,
        start_time: int = None,
        end_time: int = None
    ) -> requests.Response:
        """
        獲取 K 線數據

        Args:
            symbol: 交易對
            interval: K 線間隔 (1m, 5m, 1h, 1d 等)
            limit: 返回數量
            start_time: 開始時間（毫秒時間戳）
            end_time: 結束時間（毫秒時間戳）
        """
        params = {'symbol': symbol, 'interval': interval, 'limit': limit}
        if start_time:
            params['startTime'] = start_time
        if end_time:
            params['endTime'] = end_time
        return self._request('GET', '/api/v3/klines', params=params)

    def get_24hr_ticker(self, symbol: str = None) -> requests.Response:
        """
        獲取 24 小時價格變動統計

        Args:
            symbol: 交易對（可選，不提供則返回所有交易對）
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._request('GET', '/api/v3/ticker/24hr', params=params)

    # ==================== 需要認證的 API ====================

    def get_account_info(self) -> requests.Response:
        """獲取帳戶資訊（需要簽名）"""
        return self._request('GET', '/api/v3/account', signed=True)

    def test_new_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float = None,
        price: float = None,
        time_in_force: str = 'GTC'
    ) -> requests.Response:
        """
        測試下單（不會實際成交）

        Args:
            symbol: 交易對
            side: BUY 或 SELL
            order_type: LIMIT, MARKET 等
            quantity: 數量
            price: 價格（限價單必填）
            time_in_force: 有效期類型
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type
        }

        if quantity:
            params['quantity'] = quantity

        if order_type == 'LIMIT':
            params['timeInForce'] = time_in_force
            params['price'] = price

        return self._request('POST', '/api/v3/order/test', params=params, signed=True)

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float = None,
        quote_order_qty: float = None,
        price: float = None,
        time_in_force: str = 'GTC'
    ) -> requests.Response:
        """
        創建訂單

        Args:
            symbol: 交易對
            side: BUY 或 SELL
            order_type: LIMIT, MARKET 等
            quantity: 數量
            quote_order_qty: 報價資產數量（市價單可用）
            price: 價格（限價單必填）
            time_in_force: 有效期類型
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type
        }

        if quantity:
            params['quantity'] = quantity
        elif quote_order_qty:
            params['quoteOrderQty'] = quote_order_qty

        if order_type == 'LIMIT':
            params['timeInForce'] = time_in_force
            params['price'] = price

        return self._request('POST', '/api/v3/order', params=params, signed=True)

    def get_order(self, symbol: str, order_id: int) -> requests.Response:
        """
        查詢訂單

        Args:
            symbol: 交易對
            order_id: 訂單 ID
        """
        params = {'symbol': symbol, 'orderId': order_id}
        return self._request('GET', '/api/v3/order', params=params, signed=True)

    def cancel_order(self, symbol: str, order_id: int) -> requests.Response:
        """
        取消訂單

        Args:
            symbol: 交易對
            order_id: 訂單 ID
        """
        params = {'symbol': symbol, 'orderId': order_id}
        return self._request('DELETE', '/api/v3/order', params=params, signed=True)

    def get_open_orders(self, symbol: str = None) -> requests.Response:
        """
        查詢當前掛單

        Args:
            symbol: 交易對（可選）
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._request('GET', '/api/v3/openOrders', params=params, signed=True)

    def get_all_orders(self, symbol: str, limit: int = 500) -> requests.Response:
        """
        查詢所有訂單

        Args:
            symbol: 交易對
            limit: 返回數量
        """
        params = {'symbol': symbol, 'limit': limit}
        return self._request('GET', '/api/v3/allOrders', params=params, signed=True)

    # ==================== 工具方法 ====================

    def close(self):
        """關閉 Session"""
        self.session.close()
