# Issue Analysis

這是一個基於機器學習的問題分析系統，可以從問題標題自動判別子系統與可能的技術根本原因。

## 功能特點

- 從問題標題自動預測子系統
- 提供最可能的技術根本原因及其機率
- 提供網頁界面進行互動式預測
- 支援結果複製與郵寄功能

## 專案結構

```
issue-analysis/
├── data/                      # 訓練數據
│   └── cleaned_issues_data_new.csv
├── docs/                      # 文檔與評估報告
│   └── model_evaluation/
│       ├── model_evaluation_report.txt
│       ├── model_files_status.txt
│       └── predict_from_title_new.py
├── models/                    # 訓練好的模型
│   ├── subsystem_classification_model_new.joblib
│   ├── subsystem_tfidf_vectorizer_new.joblib
│   ├── subsystem_label_encoder_new.joblib
│   ├── root_cause_prediction_model_new.joblib
│   ├── root_cause_tfidf_vectorizer_new.joblib
│   └── root_cause_label_encoder_new.joblib
├── src/                       # 源代碼
│   ├── app.py                 # Flask 應用程式
│   ├── predict.py             # 預測腳本
│   └── templates/
│       └── index.html         # 網頁界面
├── app.yaml                   # Google App Engine 配置
└── requirements.txt           # 依賴套件
```

## 安裝與使用

### 本地運行

1. 克隆此儲存庫
2. 安裝依賴套件：
   ```
   pip install -r requirements.txt
   ```
3. 運行 Flask 應用程式：
   ```
   cd issue-analysis
   python src/app.py
   ```
4. 在瀏覽器中訪問 `http://localhost:8080`

### 使用預測腳本

您也可以直接使用預測腳本進行命令行預測：

```python
from src.predict import predict_from_title

# 預測單個標題
title = "System fails to boot after BIOS update"
subsystem, top_subsystems, top_root_causes = predict_from_title(title)
```

## 模型效能

- 子系統分類模型準確率：67.5%
- 技術根本原因預測模型準確率：57.2%

詳細的評估報告可在 `docs/model_evaluation/model_evaluation_report.txt` 中查看。

## 技術細節

- 使用 TF-IDF 進行文本特徵提取
- 子系統分類使用隨機森林分類器
- 技術根本原因預測使用邏輯回歸分類器
- 使用 Flask 框架開發網頁應用程式
- 支援 Google App Engine 部署
