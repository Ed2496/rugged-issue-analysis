import joblib
import re
import numpy as np
import pandas as pd

# 載入模型和相關檔案
subsystem_model = joblib.load('/home/ubuntu/subsystem_classification_model_new.joblib')
subsystem_vectorizer = joblib.load('/home/ubuntu/subsystem_tfidf_vectorizer_new.joblib')
subsystem_encoder = joblib.load('/home/ubuntu/subsystem_label_encoder_new.joblib')

root_cause_model = joblib.load('/home/ubuntu/root_cause_prediction_model_new.joblib')
root_cause_vectorizer = joblib.load('/home/ubuntu/root_cause_tfidf_vectorizer_new.joblib')
root_cause_encoder = joblib.load('/home/ubuntu/root_cause_label_encoder_new.joblib')

def preprocess_text(text):
    if isinstance(text, str):
        # 移除特殊字元，保留字母、數字和空格
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        # 轉換為小寫
        text = text.lower()
        # 移除多餘空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ""

def predict_subsystem(title):
    # 預處理標題
    processed_title = preprocess_text(title)
    
    # 轉換為TF-IDF特徵
    title_tfidf = subsystem_vectorizer.transform([processed_title])
    
    # 預測子系統
    subsystem_encoded = subsystem_model.predict(title_tfidf)[0]
    subsystem = subsystem_encoder.classes_[subsystem_encoded]
    
    # 獲取預測機率
    subsystem_probs = subsystem_model.predict_proba(title_tfidf)[0]
    
    # 獲取前5個最可能的子系統及其機率
    top_indices = subsystem_probs.argsort()[-5:][::-1]
    top_subsystems = [(subsystem_encoder.classes_[i], subsystem_probs[i]) for i in top_indices]
    
    return subsystem, top_subsystems

def predict_root_cause(title, top_n=5):
    # 預處理標題
    processed_title = preprocess_text(title)
    
    # 轉換為TF-IDF特徵
    title_tfidf = root_cause_vectorizer.transform([processed_title])
    
    # 預測技術根本原因
    root_cause_probs = root_cause_model.predict_proba(title_tfidf)[0]
    
    # 獲取前N個最可能的技術根本原因及其機率
    top_indices = root_cause_probs.argsort()[-top_n:][::-1]
    top_root_causes = [(root_cause_encoder.classes_[i], root_cause_probs[i]) for i in top_indices]
    
    return top_root_causes

def predict_from_title(title, top_n=5):
    # 預測子系統
    subsystem, top_subsystems = predict_subsystem(title)
    
    # 預測技術根本原因
    top_root_causes = predict_root_cause(title, top_n)
    
    # 輸出結果
    print(f"標題: {title}")
    print(f"預測的子系統: {subsystem}")
    print("\n前5個最可能的子系統及其機率:")
    for i, (sub, prob) in enumerate(top_subsystems, 1):
        print(f"{i}. {sub}: {prob:.4f}")
    
    print("\n前{top_n}個最可能的技術根本原因及其機率:")
    for i, (cause, prob) in enumerate(top_root_causes, 1):
        print(f"{i}. {cause}: {prob:.4f}")
    
    return subsystem, top_subsystems, top_root_causes

# 測試範例
if __name__ == "__main__":
    # 測試標題列表
    test_titles = [
        "[SSI_M14_HW01] System fails to boot after BIOS update",
        "USB device not recognized after sleep mode",
        "Display flickering when running graphics intensive applications",
        "Battery drains quickly even when system is in sleep mode",
        "System overheating during normal operation"
    ]
    
    print("===== 預測範例 =====\n")
    for title in test_titles:
        subsystem, top_subsystems, top_root_causes = predict_from_title(title)
        print("\n" + "="*50 + "\n")
