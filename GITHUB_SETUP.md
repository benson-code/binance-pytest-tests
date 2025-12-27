# GitHub 設置與推送指南

## 當前狀態

✅ Git repository 已初始化
✅ 初始 commit 已創建
✅ GitHub CLI (gh) 已安裝
⏳ 需要進行 GitHub 認證

## 下一步：GitHub 認證與推送

### 方式 1: 使用瀏覽器認證（推薦）

```bash
# 1. 進入專案目錄
cd /Users/mac/Documents/Prj/QA/binance-pytest-tests

# 2. 進行 GitHub 認證
gh auth login

# 按照提示選擇：
# ? What account do you want to log into?
#   > GitHub.com
#
# ? What is your preferred protocol for Git operations?
#   > HTTPS
#
# ? Authenticate Git with your GitHub credentials?
#   > Yes
#
# ? How would you like to authenticate GitHub CLI?
#   > Login with a web browser
#
# 然後會給你一個 8 位數代碼，複製它
# 按 Enter 會打開瀏覽器（如果無法自動打開，手動訪問 https://github.com/login/device）
# 在瀏覽器中貼上代碼並授權
```

### 方式 2: 使用 Personal Access Token

如果無法使用瀏覽器，可以使用 Token：

```bash
# 1. 訪問 https://github.com/settings/tokens
# 2. 點擊 "Generate new token" > "Generate new token (classic)"
# 3. 設定名稱（如 "Binance Test CLI"）
# 4. 選擇權限：
#    - repo (所有)
#    - workflow
#    - admin:public_key
# 5. 點擊 "Generate token"
# 6. 複製生成的 token

# 7. 在終端執行認證
gh auth login

# 選擇：
# ? What account do you want to log into?
#   > GitHub.com
#
# ? What is your preferred protocol for Git operations?
#   > HTTPS
#
# ? Authenticate Git with your GitHub credentials?
#   > Yes
#
# ? How would you like to authenticate GitHub CLI?
#   > Paste an authentication token
#
# 貼上你的 token
```

## 認證完成後，創建 Repository 並推送

```bash
# 1. 確認已登入
gh auth status

# 2. 創建 GitHub repository（自動設置 remote 並推送）
gh repo create binance-pytest-tests \
  --public \
  --source=. \
  --description="幣安測試網 API 自動化測試框架 (Pytest) - QA Engineer 面試準備" \
  --push

# 或者，如果想創建私有 repository
gh repo create binance-pytest-tests \
  --private \
  --source=. \
  --description="幣安測試網 API 自動化測試框架 (Pytest) - QA Engineer 面試準備" \
  --push
```

## 或者手動步驟

如果上面的命令不行，可以分步執行：

```bash
# 1. 創建 repository（不推送）
gh repo create binance-pytest-tests \
  --public \
  --description="幣安測試網 API 自動化測試框架 (Pytest)"

# 2. 添加 remote
git remote add origin https://github.com/benson-code/binance-pytest-tests.git

# 3. 推送代碼
git push -u origin main
```

## 驗證推送成功

```bash
# 查看 remote
git remote -v

# 查看 repository 狀態
gh repo view

# 在瀏覽器中打開 repository
gh repo view --web
```

## Repository 將包含的內容

- ✅ 完整的 pytest 測試框架
- ✅ 35+ 個測試案例
- ✅ 功能性、API、安全性、性能測試
- ✅ HTML 報告和覆蓋率報告支援
- ✅ 一鍵啟動腳本
- ✅ 完整的文檔（README.md + QUICK_REFERENCE.md）

## 預期的 GitHub Repository URL

```
https://github.com/benson-code/binance-pytest-tests
```

## 故障排除

### 問題 1: gh 命令找不到

```bash
# 重新載入 shell 配置
source ~/.zshrc

# 或重新安裝
brew reinstall gh
```

### 問題 2: 認證失敗

```bash
# 登出並重新登入
gh auth logout
gh auth login
```

### 問題 3: Repository 已存在

```bash
# 如果 repository 已存在，刪除它
gh repo delete benson-code/binance-pytest-tests --yes

# 然後重新創建
gh repo create binance-pytest-tests --public --source=. --push
```

### 問題 4: 推送失敗

```bash
# 檢查 remote
git remote -v

# 如果 remote 不正確，移除並重新添加
git remote remove origin
git remote add origin https://github.com/benson-code/binance-pytest-tests.git

# 重新推送
git push -u origin main
```

---

**準備好了嗎？執行上面的認證步驟，然後創建你的 GitHub repository！🚀**
