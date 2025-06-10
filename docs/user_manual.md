# Issue Analysis 使用手冊

本文檔將指導您如何使用 Issue Analysis 系統進行問題分析，包括如何運行系統、進行預測以及理解預測結果。

## 系統概述

Issue Analysis 是一個基於機器學習的問題分析系統，可以從問題標題自動判別子系統與可能的技術根本原因。系統使用了兩個主要模型：
1. 子系統分類模型：預測問題所屬的子系統
2. 技術根本原因預測模型：預測可能的技術根本原因

這些模型是基於大量的歷史問題數據訓練而成，特別是那些已經被標記為 "Fixed-Code Change" 和 "Fixed-Hardware Change" 的問題。

## 使用網頁界面

### 訪問系統

1. 如果系統已部署到 Google App Engine，請訪問部署 URL（通常格式為 `https://[YOUR_PROJECT_ID].appspot.com`）
2. 如果在本地運行，請訪問 `http://localhost:8080`

### 進行預測

1. 在主頁面的輸入框中輸入問題標題
2. 點擊「預測」按鈕
3. 系統將處理您的請求並顯示預測結果

### 理解預測結果

預測結果包含以下部分：
- **問題標題**：您輸入的原始標題
- **預測的子系統**：最可能的子系統
- **前5個最可能的子系統**：按機率排序的前5個子系統及其機率
- **前5個最可能的技術根本原因**：按機率排序的前5個技術根本原因及其機率

### 使用結果

您可以：
- 點擊「複製結果」按鈕將結果複製到剪貼簿
- 點擊「郵寄結果」按鈕使用默認郵件客戶端發送結果

## 使用命令行界面

如果您偏好使用命令行或需要批量處理多個標題，可以使用預測腳本：

1. 確保您已安裝所有依賴：
   ```bash
   pip install -r requirements.txt
   ```

2. 使用 Python 腳本進行預測：
   ```python
   from src.predict import predict_from_title
   
   # 預測單個標題
   title = "System fails to boot after BIOS update"
   subsystem, top_subsystems, top_root_causes = predict_from_title(title)
   
   # 輸出結果
   print(f"預測的子系統: {subsystem}")
   print("\n前5個最可能的子系統:")
   for i, (sub, prob) in enumerate(top_subsystems, 1):
       print(f"{i}. {sub}: {prob:.4f}")
   
   print("\n前5個最可能的技術根本原因:")
   for i, (cause, prob) in enumerate(top_root_causes, 1):
       print(f"{i}. {cause}: {prob:.4f}")
   ```

3. 批量處理多個標題：
   ```python
   titles = [
       "System fails to boot after BIOS update",
       "USB device not recognized after sleep mode",
       "Display flickering when running graphics intensive applications"
   ]
   
   for title in titles:
       print(f"\n===== 預測: {title} =====")
       subsystem, top_subsystems, top_root_causes = predict_from_title(title)
       # 輸出結果...
   ```

## 模型效能與限制

- 子系統分類模型準確率：67.5%
- 技術根本原因預測模型準確率：57.2%

請注意以下限制：
1. 預測結果僅供參考，不應完全替代專業判斷
2. 模型基於歷史數據訓練，對於全新類型的問題可能準確率較低
3. 標題描述越詳細，預測結果通常越準確

## 故障排除

1. **網頁無法訪問**：
   - 檢查部署 URL 是否正確
   - 確認 App Engine 服務是否正常運行

2. **預測失敗**：
   - 確保輸入的標題不為空
   - 檢查網絡連接是否正常

3. **預測結果不準確**：
   - 嘗試提供更詳細的問題描述
   - 考慮使用更專業的技術術語

4. **命令行腳本錯誤**：
   - 確保所有依賴已正確安裝
   - 檢查模型文件路徑是否正確

如需更多幫助，請參考專案文檔或聯繫系統管理員。
