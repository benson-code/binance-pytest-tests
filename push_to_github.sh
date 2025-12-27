#!/bin/zsh

# 一鍵推送到 GitHub 腳本
# 使用方式: ./push_to_github.sh

echo "========================================="
echo "推送到 GitHub - 自動化腳本"
echo "========================================="

# 進入專案目錄
cd /Users/mac/Documents/Prj/QA/binance-pytest-tests

# 檢查 gh 是否已安裝
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) 未安裝"
    echo "正在安裝..."
    brew install gh
fi

# 檢查是否已登入
echo "\n檢查 GitHub 認證狀態..."
if ! gh auth status &> /dev/null; then
    echo "⚠️  尚未登入 GitHub"
    echo "\n開始認證流程..."
    echo "請按照提示操作："
    echo "  1. 選擇 GitHub.com"
    echo "  2. 選擇 HTTPS"
    echo "  3. 選擇 Yes (Authenticate Git)"
    echo "  4. 選擇 Login with a web browser"
    echo ""

    gh auth login

    if [ $? -ne 0 ]; then
        echo "❌ 認證失敗"
        exit 1
    fi

    echo "✅ 認證成功！"
else
    echo "✅ 已登入 GitHub"
    gh auth status
fi

# 顯示當前用戶
echo "\n當前 GitHub 用戶:"
gh api user --jq '.login'

# 確認 repository 名稱
REPO_NAME="binance-pytest-tests"
echo "\nRepository 名稱: $REPO_NAME"

# 詢問公開或私有
echo "\n選擇 repository 類型:"
echo "1. Public (公開 - 推薦，適合展示作品)"
echo "2. Private (私有)"
read -p "請選擇 (1/2) [預設: 1]: " repo_type

if [ "$repo_type" = "2" ]; then
    VISIBILITY="--private"
    echo "選擇: 私有 repository"
else
    VISIBILITY="--public"
    echo "選擇: 公開 repository"
fi

# 創建 repository 並推送
echo "\n正在創建 GitHub repository 並推送代碼..."

gh repo create $REPO_NAME \
  $VISIBILITY \
  --source=. \
  --description="幣安測試網 API 自動化測試框架 (Pytest) - QA Engineer 面試準備" \
  --push

if [ $? -eq 0 ]; then
    echo "\n========================================="
    echo "✅ 成功推送到 GitHub！"
    echo "========================================="

    # 獲取用戶名
    USERNAME=$(gh api user --jq '.login')
    REPO_URL="https://github.com/$USERNAME/$REPO_NAME"

    echo "\nRepository URL:"
    echo "  $REPO_URL"

    echo "\n快速連結:"
    echo "  查看 Repository: gh repo view --web"
    echo "  查看 README: $REPO_URL#readme"
    echo "  Clone 連結: $REPO_URL.git"

    echo "\n下一步建議:"
    echo "  1. 訪問 $REPO_URL"
    echo "  2. 添加 Topics (標籤)：pytest, binance, api-testing, qa, automation"
    echo "  3. 設定 .env 文件後執行測試"
    echo "  4. 將此專案加入你的 GitHub Profile"

    # 詢問是否在瀏覽器中打開
    echo ""
    read -p "是否在瀏覽器中打開 repository? (y/n) [n]: " open_browser

    if [ "$open_browser" = "y" ] || [ "$open_browser" = "Y" ]; then
        gh repo view --web
    fi

else
    echo "\n❌ 推送失敗"
    echo "\n可能的原因:"
    echo "  1. Repository 名稱已存在"
    echo "  2. 網絡連接問題"
    echo "  3. 權限問題"

    echo "\n手動步驟:"
    echo "  1. 檢查是否已有同名 repository: gh repo list"
    echo "  2. 如需刪除舊的: gh repo delete $USERNAME/$REPO_NAME"
    echo "  3. 手動創建: gh repo create $REPO_NAME $VISIBILITY"
    echo "  4. 手動推送: git push -u origin main"

    exit 1
fi

echo "\n========================================="
echo "完成！"
echo "========================================="
