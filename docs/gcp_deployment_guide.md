# Google App Engine 部署指南

本文檔將指導您如何將 Issue Analysis 專案部署到 Google App Engine，以便在雲端運行並提供公開訪問。

## 前置準備

1. 確保您已經有一個 Google Cloud Platform (GCP) 帳號。如果沒有，請前往 [Google Cloud](https://cloud.google.com/) 註冊。
2. 創建一個新的 GCP 專案或選擇一個現有的專案。
3. 確保您已經啟用了 App Engine API 和結算功能（即使在免費額度內，也需要設置結算帳戶）。
4. 安裝 Google Cloud SDK：
   - 前往 [Google Cloud SDK 下載頁面](https://cloud.google.com/sdk/docs/install)
   - 根據您的操作系統下載並安裝 SDK
   - 安裝完成後，打開終端機並運行 `gcloud init` 進行初始化設置

## 步驟 1：準備部署檔案

1. 確保您的專案結構如下：
   ```
   issue-analysis/
   ├── data/
   ├── docs/
   ├── models/
   ├── src/
   │   ├── app.py
   │   ├── predict.py
   │   └── templates/
   │       └── index.html
   ├── app.yaml
   └── requirements.txt
   ```

2. 檢查 `app.yaml` 文件，確保內容如下：
   ```yaml
   runtime: python311
   entrypoint: gunicorn -b :$PORT src.app:app

   env_variables:
     PYTHONPATH: /app
   ```

3. 檢查 `requirements.txt` 文件，確保包含所有必要的依賴：
   ```
   Flask==2.2.3
   gunicorn==20.1.0
   joblib==1.2.0
   numpy==1.24.2
   pandas==1.5.3
   scikit-learn==1.2.2
   ```

## 步驟 2：部署到 App Engine

1. 打開命令行終端，進入 issue-analysis 專案目錄：
   ```bash
   cd path/to/issue-analysis
   ```

2. 使用 gcloud 命令部署應用：
   ```bash
   gcloud app deploy
   ```

3. 系統會提示您選擇區域。選擇一個離您的目標用戶最近的區域，例如：
   - `asia-east1` (台灣)
   - `asia-northeast1` (東京)
   - `us-central1` (愛荷華)

4. 確認部署設置後，輸入 `y` 開始部署。

5. 部署過程可能需要幾分鐘時間。完成後，您會看到部署成功的訊息和應用的 URL。

## 步驟 3：訪問您的應用

1. 部署完成後，您可以使用以下命令在瀏覽器中打開您的應用：
   ```bash
   gcloud app browse
   ```

2. 或者直接訪問部署成功訊息中提供的 URL，通常格式為：
   `https://[YOUR_PROJECT_ID].appspot.com`

## 步驟 4：監控和管理

1. 您可以在 Google Cloud Console 的 App Engine 頁面監控您的應用：
   - 訪問 [https://console.cloud.google.com/appengine](https://console.cloud.google.com/appengine)
   - 選擇您的專案
   - 查看儀表板、日誌、版本等信息

2. 查看應用日誌：
   ```bash
   gcloud app logs tail
   ```

## 注意事項

1. **費用考量**：
   - App Engine 提供免費額度，但超出後會產生費用
   - 監控您的用量，避免意外收費
   - 考慮設置預算提醒

2. **性能優化**：
   - 首次請求可能較慢（冷啟動）
   - 考慮使用 App Engine 的自動擴展功能

3. **安全性**：
   - 定期更新依賴包
   - 考慮添加身份驗證機制

4. **更新應用**：
   - 修改代碼後，重新運行 `gcloud app deploy` 即可更新
   - 每次部署會創建新版本，舊版本會保留

## 故障排除

1. **部署失敗**：
   - 檢查 `app.yaml` 和 `requirements.txt` 是否正確
   - 查看部署日誌了解詳細錯誤信息

2. **應用啟動失敗**：
   - 使用 `gcloud app logs tail` 查看運行時錯誤
   - 確保所有依賴都已正確安裝

3. **找不到模型文件**：
   - 確保模型文件已正確上傳
   - 檢查文件路徑是否正確

如果您遇到其他問題，請參考 [Google App Engine 文檔](https://cloud.google.com/appengine/docs) 或在 Google Cloud 社區尋求幫助。
