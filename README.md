# Binance Testnet API 自動化測試框架 (Pytest)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Testing-green?logo=pytest&logoColor=white)
![GitHub Stars](https://img.shields.io/github/stars/benson-code/binance-pytest-tests?style=social)
![GitHub Forks](https://img.shields.io/github/forks/benson-code/binance-pytest-tests?style=social)

> 使用 Pytest 建立的幣安測試網 API 自動化測試框架，包含 **35+ 測試案例**，涵蓋功能性、API、安全性及性能測試。適用於 QA Engineer 面試準備與實際測試工作。

## 專案特色

- 完整的 API 測試覆蓋（功能性、安全性、性能測試）
- 基於 Pytest 的專業測試框架
- 自動化測試報告生成（HTML + 覆蓋率）
- 完整的文檔和快速開始指南
- 支援並行測試執行
- 真實的 Binance Testnet API 集成

## 專案結構

```
binance-pytest-tests/
├── config.py                 # 配置文件
├── conftest.py              # Pytest fixtures 和配置
├── requirements.txt         # Python 依賴套件
├── pytest.ini               # Pytest 配置
├── .env.example             # 環境變數範本
├── utils/
│   ├── __init__.py
│   └── binance_client.py    # Binance API 客戶端封裝
├── tests/
│   ├── __init__.py
│   ├── test_functional.py   # 功能性測試
│   ├── test_api_trading.py  # API 交易測試（需認證）
│   ├── test_security.py     # 安全性測試
│   └── test_performance.py  # 性能測試
└── reports/                 # 測試報告目錄
    ├── report.html          # HTML 測試報告
    ├── coverage/            # 代碼覆蓋率報告
    └── pytest.log           # 測試日誌
```

## 測試覆蓋範圍

### 功能性測試 (test_functional.py)
- ✅ API 連線測試 (Ping)
- ✅ 伺服器時間查詢
- ✅ 交易所資訊查詢
- ✅ 深度資訊查詢
- ✅ 最近交易查詢
- ✅ K 線數據查詢
- ✅ 24 小時價格統計
- ✅ 多交易對測試

### API 交易測試 (test_api_trading.py)
- ✅ 帳戶資訊查詢
- ✅ 虛擬資金驗證
- ✅ 測試下單（不實際成交）
- ✅ 創建限價單
- ✅ 創建並取消訂單
- ✅ 查詢訂單狀態
- ✅ 查詢所有訂單
- ✅ 完整交易流程測試
- ✅ 負面測試（無效參數、不存在訂單等）

### 安全性測試 (test_security.py)
- ✅ 缺少簽名驗證
- ✅ 錯誤簽名驗證
- ✅ 無效 API Key 驗證
- ✅ 過期時間戳驗證
- ✅ SQL 注入測試
- ✅ XSS 攻擊測試
- ✅ 參數驗證測試
- ✅ HTTPS/TLS 安全測試

### 性能測試 (test_performance.py)
- ✅ 響應時間測試
- ✅ 市場數據查詢性能
- ✅ 大量數據查詢性能
- ✅ 併發請求測試
- ✅ 持續負載測試
- ✅ 速率限制測試
- ✅ 數據一致性測試

## 安裝與設定

### 1. 環境需求
- Python 3.8 或更高版本
- macOS (zsh shell)
- 網絡連接

### 2. 安裝依賴

```bash
# 進入專案目錄
cd /Users/mac/Documents/Prj/QA/binance-pytest-tests

# 建議：創建虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝依賴套件
pip3 install -r requirements.txt
```

### 3. 配置 API 憑證

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 文件，填入你的 API 憑證
nano .env
```

在 `.env` 文件中填入：
```bash
BINANCE_BASE_URL=https://testnet.binance.vision
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
```

**如何獲取 API 憑證：**
1. 訪問 https://testnet.binance.vision/
2. 使用 GitHub 帳號登入
3. 生成 API Key 和 Secret Key
4. 複製到 `.env` 文件中

## 執行測試

### 基本執行方式

```bash
# 執行所有測試
pytest

# 執行特定測試文件
pytest tests/test_functional.py

# 執行特定測試類別
pytest tests/test_functional.py::TestBasicFunctionality

# 執行特定測試函數
pytest tests/test_functional.py::TestBasicFunctionality::test_ping_connection
```

### 使用標記執行測試

```bash
# 只執行冒煙測試
pytest -m smoke

# 執行 P0 優先級測試
pytest -m p0

# 執行功能性測試
pytest -m functional

# 執行 API 測試（需要 API 憑證）
pytest -m api

# 執行安全性測試
pytest -m security

# 執行性能測試
pytest -m performance

# 組合標記（P0 且功能性測試）
pytest -m "p0 and functional"

# 排除慢速測試
pytest -m "not slow"
```

### 詳細輸出與報告

```bash
# 詳細輸出 (-v)
pytest -v

# 顯示 print 輸出 (-s)
pytest -s

# 顯示測試進度百分比
pytest --tb=short

# 失敗時立即停止
pytest -x

# 失敗後繼續執行 N 次失敗
pytest --maxfail=3

# 生成 HTML 報告
pytest --html=reports/report.html --self-contained-html

# 生成覆蓋率報告
pytest --cov=. --cov-report=html:reports/coverage
```

### 並行執行（加速測試）

```bash
# 使用多核心並行執行（需安裝 pytest-xdist）
pytest -n 4  # 使用 4 個 worker

# 自動檢測 CPU 核心數
pytest -n auto
```

### 進階執行選項

```bash
# 重新執行失敗的測試
pytest --lf  # last failed

# 只執行失敗的測試，然後執行所有測試
pytest --ff  # failed first

# 顯示最慢的 10 個測試
pytest --durations=10

# 乾跑（不實際執行，只顯示會執行哪些測試）
pytest --collect-only
```

## 測試報告

### HTML 報告

執行測試後，在 `reports/report.html` 查看詳細的 HTML 測試報告：

```bash
# 執行測試並生成報告
pytest --html=reports/report.html --self-contained-html

# 在瀏覽器中查看報告（如果可以在 Mac 上操作）
# 或將報告複製到 Windows 端查看
```

### 覆蓋率報告

```bash
# 生成覆蓋率報告
pytest --cov=. --cov-report=html:reports/coverage

# 查看報告
# 複製 reports/coverage/index.html 到 Windows 端瀏覽器查看
```

### 日誌文件

測試執行日誌保存在 `reports/pytest.log`：

```bash
# 查看最近的測試日誌
tail -f reports/pytest.log

# 查看完整日誌
cat reports/pytest.log
```

## 常見使用場景

### 場景 1: 快速冒煙測試

```bash
# 執行 P0 優先級的冒煙測試（不需要 API 憑證）
pytest -m "smoke and p0" -v
```

### 場景 2: 完整功能測試

```bash
# 執行所有功能性和 API 測試（需要 API 憑證）
pytest -m "functional or api" -v --html=reports/report.html
```

### 場景 3: 安全性檢查

```bash
# 執行所有安全性測試
pytest -m security -v -s
```

### 場景 4: 性能基準測試

```bash
# 執行性能測試（排除慢速測試）
pytest -m "performance and not slow" -v

# 執行完整性能測試（包含慢速測試）
pytest -m performance -v --durations=10
```

### 場景 5: 持續集成 (CI) 執行

```bash
# CI 友好的執行方式
pytest -m "not slow" --tb=short --maxfail=5 -v \
  --html=reports/report.html --self-contained-html \
  --cov=. --cov-report=html:reports/coverage
```

## 開發與擴展

### 添加新測試

1. 在 `tests/` 目錄下創建或編輯測試文件
2. 使用適當的標記（@pytest.mark）
3. 使用 fixtures（從 conftest.py）
4. 遵循命名規範：`test_*.py`

範例：

```python
import pytest
from utils.binance_client import BinanceClient

@pytest.mark.functional
@pytest.mark.p1
def test_my_new_feature(binance_client: BinanceClient):
    """測試新功能"""
    response = binance_client.ping()
    assert response.status_code == 200
```

### 添加新 Fixtures

在 `conftest.py` 中添加共享的 fixtures：

```python
@pytest.fixture
def my_fixture():
    """新的 fixture"""
    # 設置
    data = "test data"
    yield data
    # 清理（如需要）
```

### 自定義配置

在 `config.py` 中添加配置項：

```python
class Config:
    MY_NEW_CONFIG = os.getenv('MY_CONFIG', 'default_value')
```

## 故障排除

### 問題 1: 找不到模組

```bash
# 確保已安裝依賴
pip3 install -r requirements.txt

# 或單獨安裝
pip3 install pytest requests python-dotenv
```

### 問題 2: API 憑證未配置

```bash
# 確認 .env 文件存在且正確配置
cat .env

# 或跳過需要 API 憑證的測試
pytest -m "not api"
```

### 問題 3: SSL 憑證錯誤

```bash
# 更新 certifi
pip3 install --upgrade certifi

# 或臨時跳過 SSL 驗證（不推薦）
export PYTHONHTTPSVERIFY=0
```

### 問題 4: 速率限制

如果遇到 429 錯誤（Too Many Requests）：

```bash
# 等待幾分鐘後重試
# 或降低並行數
pytest -n 2  # 而非 -n 4
```

## 最佳實踐

1. **先執行冒煙測試**：確保基礎功能正常
   ```bash
   pytest -m smoke
   ```

2. **使用適當的標記**：避免執行不必要的測試
   ```bash
   pytest -m "p0 and not slow"
   ```

3. **定期查看報告**：檢查 HTML 報告了解測試詳情

4. **關注失敗測試**：使用 `--lf` 重新執行失敗的測試

5. **保持測試獨立**：每個測試應能獨立執行

6. **清理測試數據**：測試後取消創建的訂單

## CI/CD 整合範例

### GitHub Actions

創建 `.github/workflows/test.yml`：

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        env:
          BINANCE_API_KEY: ${{ secrets.BINANCE_API_KEY }}
          BINANCE_SECRET_KEY: ${{ secrets.BINANCE_SECRET_KEY }}
        run: |
          pytest -m "not slow" --html=reports/report.html
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: reports/
```

## 測試統計

執行完整測試套件後，預期結果：

- **總測試案例**: ~40 個
- **執行時間**:
  - 不含慢速測試: ~30 秒
  - 包含慢速測試: ~2-3 分鐘
- **覆蓋率**: 預期 >80%

## 聯絡與貢獻

此專案為 QA Engineer 面試準備與學習用途。

**相關資源**:
- 幣安測試網: https://testnet.binance.vision/
- Binance API 文檔: https://binance-docs.github.io/apidocs/spot/en/
- Pytest 文檔: https://docs.pytest.org/

## 授權

此專案僅供學習和測試使用。

---

**Happy Testing! 🚀**
