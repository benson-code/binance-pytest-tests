"""
API 測試 - 交易相關（需要 API 認證）
"""
import pytest
import time
from utils.binance_client import BinanceClient
from config import Config


@pytest.mark.api
@pytest.mark.p0
class TestAccountAPI:
    """帳戶 API 測試"""

    @pytest.mark.skipif(
        not Config.is_configured(),
        reason="需要設定 API 憑證 (API_KEY 和 SECRET_KEY)"
    )
    def test_get_account_info(self, binance_client: BinanceClient):
        """TC-A001: 獲取帳戶資訊"""
        response = binance_client.get_account_info()

        assert response.status_code == 200, f"狀態碼應為 200，實際 {response.status_code}"
        data = response.json()

        # 驗證帳戶資訊結構
        assert 'balances' in data, "響應應包含 balances"
        assert isinstance(data['balances'], list), "balances 應為陣列"

        # 驗證餘額結構
        if len(data['balances']) > 0:
            balance = data['balances'][0]
            assert 'asset' in balance
            assert 'free' in balance
            assert 'locked' in balance

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_get_account_balances_non_zero(self, binance_client: BinanceClient):
        """TC-A002: 驗證帳戶有虛擬資金"""
        response = binance_client.get_account_info()
        assert response.status_code == 200

        data = response.json()
        balances = data['balances']

        # 篩選非零餘額
        non_zero_balances = [
            b for b in balances if float(b['free']) > 0 or float(b['locked']) > 0
        ]

        assert len(non_zero_balances) > 0, "測試帳戶應有虛擬資金"


@pytest.mark.api
@pytest.mark.p0
class TestOrderAPI:
    """訂單 API 測試"""

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_new_order_test(self, binance_client: BinanceClient, order_params: dict):
        """TC-A003: 測試下單（不實際成交）"""
        response = binance_client.test_new_order(
            symbol=order_params['symbol'],
            side=order_params['side'],
            order_type=order_params['order_type'],
            quantity=order_params['quantity'],
            price=order_params['price'],
            time_in_force=order_params['time_in_force']
        )

        assert response.status_code == 200
        # 測試下單返回空 JSON
        assert response.json() == {}

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_create_limit_order(self, binance_client: BinanceClient, order_params: dict):
        """TC-A004: 創建限價單"""
        response = binance_client.create_order(
            symbol=order_params['symbol'],
            side=order_params['side'],
            order_type=order_params['order_type'],
            quantity=order_params['quantity'],
            price=order_params['price'],
            time_in_force=order_params['time_in_force']
        )

        assert response.status_code == 200, f"創建訂單失敗: {response.text}"
        data = response.json()

        # 驗證訂單響應
        assert 'orderId' in data, "響應應包含 orderId"
        assert 'status' in data, "響應應包含 status"
        assert data['symbol'] == order_params['symbol']
        assert data['side'] == order_params['side']

        # 保存訂單 ID 用於後續測試
        order_id = data['orderId']

        # 查詢訂單
        time.sleep(1)  # 等待訂單處理
        query_response = binance_client.get_order(
            symbol=order_params['symbol'],
            order_id=order_id
        )
        assert query_response.status_code == 200

        # 取消訂單（清理）
        cancel_response = binance_client.cancel_order(
            symbol=order_params['symbol'],
            order_id=order_id
        )
        assert cancel_response.status_code == 200

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_create_and_cancel_order(
        self, binance_client: BinanceClient, order_params: dict
    ):
        """TC-A005: 創建並取消訂單"""
        # 1. 創建訂單
        create_response = binance_client.create_order(
            symbol=order_params['symbol'],
            side=order_params['side'],
            order_type=order_params['order_type'],
            quantity=order_params['quantity'],
            price=order_params['price'],
            time_in_force=order_params['time_in_force']
        )

        assert create_response.status_code == 200
        order_id = create_response.json()['orderId']

        # 2. 取消訂單
        time.sleep(1)
        cancel_response = binance_client.cancel_order(
            symbol=order_params['symbol'],
            order_id=order_id
        )

        assert cancel_response.status_code == 200
        cancel_data = cancel_response.json()
        assert cancel_data['orderId'] == order_id
        assert cancel_data['status'] == 'CANCELED'

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_query_order(self, binance_client: BinanceClient, order_params: dict):
        """TC-A006: 查詢訂單狀態"""
        # 先創建訂單
        create_response = binance_client.create_order(
            symbol=order_params['symbol'],
            side=order_params['side'],
            order_type=order_params['order_type'],
            quantity=order_params['quantity'],
            price=order_params['price']
        )
        assert create_response.status_code == 200
        order_id = create_response.json()['orderId']

        # 查詢訂單
        time.sleep(1)
        query_response = binance_client.get_order(
            symbol=order_params['symbol'],
            order_id=order_id
        )

        assert query_response.status_code == 200
        order_data = query_response.json()

        # 驗證訂單資訊
        assert order_data['orderId'] == order_id
        assert order_data['symbol'] == order_params['symbol']
        assert order_data['side'] == order_params['side']
        assert order_data['type'] == order_params['order_type']
        assert order_data['status'] in ['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED']

        # 清理：取消訂單
        binance_client.cancel_order(
            symbol=order_params['symbol'],
            order_id=order_id
        )

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_get_all_orders(self, binance_client: BinanceClient, test_symbol: str):
        """TC-A007: 查詢所有訂單"""
        response = binance_client.get_all_orders(symbol=test_symbol, limit=10)

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list), "響應應為陣列"
        # 注意：可能為空陣列（如果沒有歷史訂單）


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.p0
class TestCompleteTradeFlow:
    """完整交易流程測試"""

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    @pytest.mark.slow
    def test_complete_trade_flow(self, binance_client: BinanceClient, test_symbol: str):
        """TC-I001: 完整交易流程 - 查詢餘額 > 下單 > 查詢 > 取消 > 驗證"""

        # 1. 查詢初始帳戶餘額
        initial_account = binance_client.get_account_info()
        assert initial_account.status_code == 200
        print("\n初始帳戶餘額已記錄")

        # 2. 下限價買單（低於市價，不會成交）
        order_response = binance_client.create_order(
            symbol=test_symbol,
            side='BUY',
            order_type='LIMIT',
            quantity=0.001,
            price=20000,
            time_in_force='GTC'
        )
        assert order_response.status_code == 200
        order_id = order_response.json()['orderId']
        print(f"訂單已創建: {order_id}")

        # 3. 查詢訂單狀態
        time.sleep(2)
        query_response = binance_client.get_order(symbol=test_symbol, order_id=order_id)
        assert query_response.status_code == 200
        order_data = query_response.json()
        assert order_data['status'] == 'NEW'
        print(f"訂單狀態: {order_data['status']}")

        # 4. 查詢當前掛單
        open_orders = binance_client.get_open_orders(symbol=test_symbol)
        assert open_orders.status_code == 200
        open_orders_data = open_orders.json()
        order_ids = [o['orderId'] for o in open_orders_data]
        assert order_id in order_ids, "訂單應出現在未成交列表中"

        # 5. 取消訂單
        cancel_response = binance_client.cancel_order(symbol=test_symbol, order_id=order_id)
        assert cancel_response.status_code == 200
        assert cancel_response.json()['status'] == 'CANCELED'
        print("訂單已取消")

        # 6. 再次查詢訂單確認已取消
        time.sleep(1)
        final_query = binance_client.get_order(symbol=test_symbol, order_id=order_id)
        assert final_query.status_code == 200
        assert final_query.json()['status'] == 'CANCELED'

        # 7. 查詢最終餘額
        final_account = binance_client.get_account_info()
        assert final_account.status_code == 200
        print("交易流程完成")


@pytest.mark.api
@pytest.mark.negative
@pytest.mark.p1
class TestNegativeOrderCases:
    """負面測試 - 訂單相關"""

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_cancel_non_existent_order(self, binance_client: BinanceClient, test_symbol: str):
        """TC-N001: 取消不存在的訂單"""
        fake_order_id = 999999999

        response = binance_client.cancel_order(
            symbol=test_symbol,
            order_id=fake_order_id
        )

        # 應返回錯誤
        assert response.status_code in [400, 404], "取消不存在的訂單應返回錯誤"

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_invalid_symbol_order(self, binance_client: BinanceClient):
        """TC-N002: 使用無效交易對下單"""
        response = binance_client.create_order(
            symbol='INVALIDPAIR',
            side='BUY',
            order_type='MARKET',
            quantity=0.001
        )

        assert response.status_code == 400, "無效交易對應返回 400"
        error_data = response.json()
        assert 'code' in error_data
        assert 'msg' in error_data

    @pytest.mark.skipif(not Config.is_configured(), reason="需要 API 憑證")
    def test_negative_quantity_order(self, binance_client: BinanceClient, test_symbol: str):
        """TC-N003: 使用負數數量下單"""
        response = binance_client.test_new_order(
            symbol=test_symbol,
            side='BUY',
            order_type='MARKET',
            quantity=-0.001
        )

        assert response.status_code == 400, "負數數量應返回 400"
