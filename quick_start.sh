#!/bin/zsh

# 幣安測試網 Pytest 快速啟動腳本
# 使用方式: ./quick_start.sh

echo "========================================="
echo "幣安測試網 API 自動化測試框架"
echo "========================================="

# 檢查 Python 版本
echo "\n檢查 Python 版本..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ 錯誤: 未找到 Python 3"
    echo "請先安裝 Python 3.8 或更高版本"
    exit 1
fi

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "\n創建虛擬環境..."
    python3 -m venv venv
    echo "✅ 虛擬環境已創建"
fi

# 啟動虛擬環境
echo "\n啟動虛擬環境..."
source venv/bin/activate

# 安裝依賴
echo "\n安裝依賴套件..."
pip3 install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ 依賴安裝失敗"
    exit 1
fi

echo "✅ 依賴安裝完成"

# 檢查 .env 文件
if [ ! -f ".env" ]; then
    echo "\n⚠️  警告: .env 文件不存在"
    echo "正在創建 .env 文件..."
    cp .env.example .env
    echo "✅ .env 文件已創建"
    echo ""
    echo "請編輯 .env 文件，填入你的 API 憑證："
    echo "  nano .env"
    echo ""
    echo "如何獲取 API 憑證："
    echo "  1. 訪問 https://testnet.binance.vision/"
    echo "  2. 使用 GitHub 帳號登入"
    echo "  3. 生成 API Key 和 Secret Key"
    echo "  4. 複製到 .env 文件中"
    echo ""
    read -p "按 Enter 繼續（或 Ctrl+C 取消）..."
fi

# 創建報告目錄
mkdir -p reports

# 顯示選單
echo "\n========================================="
echo "選擇測試選項:"
echo "========================================="
echo "1. 🚀 快速冒煙測試 (不需要 API 憑證)"
echo "2. 🧪 完整功能測試 (需要 API 憑證)"
echo "3. 🔒 安全性測試"
echo "4. ⚡ 性能測試"
echo "5. 📊 生成完整報告"
echo "6. 🔍 查看測試列表"
echo "7. 🛠️  自定義執行"
echo "0. ❌ 退出"
echo "========================================="

read -p "請選擇 (0-7): " choice

case $choice in
    1)
        echo "\n執行冒煙測試..."
        pytest -m smoke -v
        ;;
    2)
        echo "\n執行完整功能測試..."
        pytest -m "functional or api" -v --html=reports/report.html --self-contained-html
        echo "\n✅ 報告已生成: reports/report.html"
        ;;
    3)
        echo "\n執行安全性測試..."
        pytest -m security -v -s
        ;;
    4)
        echo "\n執行性能測試..."
        pytest -m "performance and not slow" -v
        ;;
    5)
        echo "\n執行所有測試並生成完整報告..."
        pytest -v --html=reports/report.html --self-contained-html \
               --cov=. --cov-report=html:reports/coverage \
               --cov-report=term-missing
        echo "\n✅ HTML 報告: reports/report.html"
        echo "✅ 覆蓋率報告: reports/coverage/index.html"
        ;;
    6)
        echo "\n測試列表:"
        pytest --collect-only -q
        ;;
    7)
        echo "\n請輸入 pytest 命令 (例如: -m p0 -v):"
        read custom_args
        pytest $custom_args
        ;;
    0)
        echo "\n再見！"
        exit 0
        ;;
    *)
        echo "\n❌ 無效選擇"
        exit 1
        ;;
esac

echo "\n========================================="
echo "測試完成！"
echo "========================================="
