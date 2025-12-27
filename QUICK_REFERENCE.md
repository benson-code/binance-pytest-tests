# Pytest 快速參考指南

## 一鍵啟動

```bash
cd /Users/mac/Documents/Prj/QA/binance-pytest-tests
./quick_start.sh
```

## 常用命令速查

### 基本執行

```bash
# 執行所有測試
pytest

# 詳細輸出
pytest -v

# 顯示 print 輸出
pytest -s

# 失敗時停止
pytest -x
```

### 按標記執行

```bash
# 冒煙測試 (無需 API 憑證)
pytest -m smoke

# P0 優先級測試
pytest -m p0

# 功能性測試
pytest -m functional

# API 測試 (需要 API 憑證)
pytest -m api

# 安全性測試
pytest -m security

# 性能測試
pytest -m performance

# 排除慢速測試
pytest -m "not slow"
```

### 按文件/類別/函數執行

```bash
# 執行特定文件
pytest tests/test_functional.py

# 執行特定類別
pytest tests/test_functional.py::TestBasicFunctionality

# 執行特定函數
pytest tests/test_functional.py::TestBasicFunctionality::test_ping_connection

# 關鍵字匹配
pytest -k "ping"  # 執行名稱包含 "ping" 的測試
```

### 報告生成

```bash
# HTML 報告
pytest --html=reports/report.html --self-contained-html

# 覆蓋率報告
pytest --cov=. --cov-report=html:reports/coverage

# 顯示最慢的 10 個測試
pytest --durations=10

# JSON 報告
pytest --json-report --json-report-file=reports/report.json
```

### 失敗處理

```bash
# 重新執行上次失敗的測試
pytest --lf

# 先執行失敗的，再執行其他的
pytest --ff

# 失敗後繼續執行（最多 3 個失敗）
pytest --maxfail=3
```

### 並行執行

```bash
# 使用 4 個 worker
pytest -n 4

# 自動檢測 CPU 核心數
pytest -n auto
```

## 環境設定

### 初次設定

```bash
# 1. 創建虛擬環境
python3 -m venv venv

# 2. 啟動虛擬環境
source venv/bin/activate

# 3. 安裝依賴
pip3 install -r requirements.txt

# 4. 設定環境變數
cp .env.example .env
nano .env  # 填入 API 憑證
```

### 每次使用

```bash
# 啟動虛擬環境
source venv/bin/activate

# 執行測試
pytest -m smoke

# 退出虛擬環境
deactivate
```

## 常用組合

### 快速驗證（無需 API 憑證）

```bash
pytest -m "smoke and p0" -v
```

### 完整功能測試（需要 API 憑證）

```bash
pytest -m "functional or api" -v --html=reports/report.html
```

### CI/CD 友好執行

```bash
pytest -m "not slow" --tb=short --maxfail=5 -v \
  --html=reports/report.html --self-contained-html
```

### 完整報告生成

```bash
pytest -v --html=reports/report.html --self-contained-html \
  --cov=. --cov-report=html:reports/coverage
```

## 標記 (Markers) 說明

| 標記 | 說明 | 範例 |
|------|------|------|
| `smoke` | 冒煙測試，快速驗證 | `pytest -m smoke` |
| `functional` | 功能性測試 | `pytest -m functional` |
| `api` | API 測試（需認證） | `pytest -m api` |
| `security` | 安全性測試 | `pytest -m security` |
| `performance` | 性能測試 | `pytest -m performance` |
| `integration` | 整合測試 | `pytest -m integration` |
| `negative` | 負面測試 | `pytest -m negative` |
| `p0` | 優先級 P0 (Critical) | `pytest -m p0` |
| `p1` | 優先級 P1 (High) | `pytest -m p1` |
| `p2` | 優先級 P2 (Medium) | `pytest -m p2` |
| `slow` | 執行時間較長 | `pytest -m "not slow"` |

## Fixtures 說明

| Fixture | Scope | 說明 |
|---------|-------|------|
| `binance_client` | session | 整個測試會話共用一個客戶端 |
| `binance_client_function` | function | 每個測試函數創建新客戶端 |
| `test_symbol` | session | 預設測試交易對 (BTCUSDT) |
| `test_symbols` | session | 測試交易對列表 |
| `order_params` | function | 測試訂單參數 |
| `market_order_params` | function | 市價單參數 |

## 故障排除

### 問題：找不到模組

```bash
# 確保在虛擬環境中
source venv/bin/activate

# 重新安裝依賴
pip3 install -r requirements.txt
```

### 問題：API 憑證未配置

```bash
# 跳過需要 API 的測試
pytest -m "not api"

# 或配置 .env 文件
nano .env
```

### 問題：測試失敗

```bash
# 查看詳細錯誤
pytest -v -s

# 只重新執行失敗的測試
pytest --lf -v

# 查看日誌
cat reports/pytest.log
```

## 測試文件說明

| 文件 | 說明 | 需要 API 憑證 |
|------|------|---------------|
| `test_functional.py` | 基礎功能測試 | ❌ 不需要 |
| `test_api_trading.py` | 交易 API 測試 | ✅ 需要 |
| `test_security.py` | 安全性測試 | 部分需要 |
| `test_performance.py` | 性能測試 | ❌ 不需要 |

## 查看測試覆蓋率

```bash
# 生成覆蓋率報告
pytest --cov=. --cov-report=html:reports/coverage

# 查看報告（需要複製到 Windows 端）
# reports/coverage/index.html
```

## 配置文件說明

| 文件 | 說明 |
|------|------|
| `pytest.ini` | Pytest 配置 |
| `conftest.py` | Fixtures 和 hooks |
| `config.py` | 測試配置 |
| `.env` | 環境變數（API 憑證） |
| `requirements.txt` | Python 依賴 |

## 實用技巧

1. **只看測試名稱，不執行**
   ```bash
   pytest --collect-only -q
   ```

2. **失敗後進入調試模式**
   ```bash
   pytest --pdb
   ```

3. **設定超時時間**
   ```bash
   pytest --timeout=60
   ```

4. **忽略特定警告**
   ```bash
   pytest -p no:warnings
   ```

5. **自定義輸出格式**
   ```bash
   pytest --tb=line  # 簡短錯誤
   pytest --tb=short # 短格式
   pytest --tb=long  # 詳細格式
   ```

## 快速測試流程

### 第一次使用

```bash
# 1. 進入目錄
cd /Users/mac/Documents/Prj/QA/binance-pytest-tests

# 2. 執行快速啟動腳本
./quick_start.sh

# 3. 選擇選項 1（冒煙測試）
```

### 日常使用

```bash
# 啟動虛擬環境
source venv/bin/activate

# 執行你需要的測試
pytest -m smoke -v

# 完成後退出
deactivate
```

---

**快速幫助**: `pytest --help`
**完整文檔**: 查看 `README.md`
