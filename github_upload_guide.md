# GitHub 上傳指南

本文檔將指導您如何將 Issue Analysis 專案上傳到 GitHub，以便進行版本控制和共享。

## 前置準備

1. 確保您已經有一個 GitHub 帳號。如果沒有，請前往 [GitHub](https://github.com/) 註冊。
2. 確保您的電腦上已安裝 Git。如果沒有，請前往 [Git 官網](https://git-scm.com/) 下載並安裝。
3. 在命令行中設置您的 Git 用戶名和電子郵件：
   ```bash
   git config --global user.name "您的用戶名"
   git config --global user.email "您的電子郵件"
   ```

## 步驟 1：創建新的 GitHub 儲存庫

1. 登入您的 GitHub 帳號。
2. 點擊右上角的 "+" 圖標，然後選擇 "New repository"。
3. 在 "Repository name" 欄位中輸入 "issue-analysis"。
4. 可選：添加描述，例如 "從問題標題自動判別子系統與技術根本原因的分析系統"。
5. 選擇儲存庫的可見性（公開或私有）。
6. 不要勾選 "Initialize this repository with a README"，因為我們已經有了 README 文件。
7. 點擊 "Create repository" 按鈕。

## 步驟 2：初始化本地 Git 儲存庫並上傳專案

1. 打開命令行終端，進入 issue-analysis 專案目錄：
   ```bash
   cd path/to/issue-analysis
   ```

2. 初始化 Git 儲存庫：
   ```bash
   git init
   ```

3. 創建 .gitignore 文件，排除不需要版本控制的文件：
   ```bash
   echo "__pycache__/" > .gitignore
   echo "*.pyc" >> .gitignore
   echo "*.pyo" >> .gitignore
   echo "*.pyd" >> .gitignore
   echo ".Python" >> .gitignore
   echo "env/" >> .gitignore
   echo "venv/" >> .gitignore
   echo ".env" >> .gitignore
   echo ".venv" >> .gitignore
   ```

4. 添加所有文件到暫存區：
   ```bash
   git add .
   ```

5. 提交變更：
   ```bash
   git commit -m "Initial commit"
   ```

6. 添加遠程儲存庫：
   ```bash
   git remote add origin https://github.com/您的用戶名/issue-analysis.git
   ```

7. 推送到 GitHub：
   ```bash
   git push -u origin main
   ```
   
   注意：如果您的 Git 默認分支是 `master` 而不是 `main`，請使用：
   ```bash
   git push -u origin master
   ```

## 步驟 3：驗證上傳

1. 前往您的 GitHub 儲存庫頁面：`https://github.com/您的用戶名/issue-analysis`
2. 確認所有文件都已成功上傳。
3. 檢查 README.md 是否正確顯示在儲存庫首頁。

## 注意事項

- 由於模型文件較大，GitHub 可能會限制單個文件的大小（通常為 100MB）。如果您遇到這個問題，可以考慮使用 [Git LFS](https://git-lfs.github.com/)（Large File Storage）來處理大文件。
- 如果您不想將模型文件上傳到 GitHub，可以修改 .gitignore 文件，添加：
  ```
  models/*.joblib
  ```
  然後在 README.md 中說明如何獲取這些模型文件。

## 後續更新

當您對專案進行修改後，可以使用以下命令將變更推送到 GitHub：

```bash
git add .
git commit -m "描述您的變更"
git push
```

這樣，您的專案就會保持最新狀態。
