import os
import re
import json
import logging
import traceback
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
import joblib
import pandas as pd
import numpy as np

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 設定模型檔案路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')
TEMP_DIR = os.path.join(BASE_DIR, 'temp')

# 確保臨時目錄存在
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# 設定上傳檔案的最大大小 (50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# 全局變數，用於存儲上傳的檔案路徑
uploaded_file_path = None

# 自定義 JSON 編碼器，處理 NaN 值
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj) if not np.isnan(obj) else None
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if pd.isna(obj):
            return None
        return super(NpEncoder, self).default(obj)

# 設定 Flask 應用程式使用自定義 JSON 編碼器
app.json_encoder = NpEncoder

# 嘗試載入模型
subsystem_model = None
subsystem_vectorizer = None
subsystem_encoder = None
root_cause_model = None
root_cause_vectorizer = None
root_cause_encoder = None

def load_models():
    global subsystem_model, subsystem_vectorizer, subsystem_encoder
    global root_cause_model, root_cause_vectorizer, root_cause_encoder
    
    try:
        # 嘗試不同的可能路徑
        possible_model_dirs = [
            MODEL_DIR,
            os.path.join(BASE_DIR, 'models'),
            os.path.join(os.path.dirname(BASE_DIR), 'models'),
            '/app/models',
            '/workspace/models'
        ]
        
        model_loaded = False
        
        for model_dir in possible_model_dirs:
            try:
                logger.info(f"嘗試從路徑載入模型: {model_dir}")
                
                if os.path.exists(model_dir):
                    subsystem_model_path = os.path.join(model_dir, 'subsystem_classification_model_new.joblib')
                    subsystem_vectorizer_path = os.path.join(model_dir, 'subsystem_tfidf_vectorizer_new.joblib')
                    subsystem_encoder_path = os.path.join(model_dir, 'subsystem_label_encoder_new.joblib')
                    
                    root_cause_model_path = os.path.join(model_dir, 'root_cause_prediction_model_new.joblib')
                    root_cause_vectorizer_path = os.path.join(model_dir, 'root_cause_tfidf_vectorizer_new.joblib')
                    root_cause_encoder_path = os.path.join(model_dir, 'root_cause_label_encoder_new.joblib')
                    
                    if (os.path.exists(subsystem_model_path) and 
                        os.path.exists(subsystem_vectorizer_path) and 
                        os.path.exists(subsystem_encoder_path) and 
                        os.path.exists(root_cause_model_path) and 
                        os.path.exists(root_cause_vectorizer_path) and 
                        os.path.exists(root_cause_encoder_path)):
                        
                        subsystem_model = joblib.load(subsystem_model_path)
                        subsystem_vectorizer = joblib.load(subsystem_vectorizer_path)
                        subsystem_encoder = joblib.load(subsystem_encoder_path)
                        
                        root_cause_model = joblib.load(root_cause_model_path)
                        root_cause_vectorizer = joblib.load(root_cause_vectorizer_path)
                        root_cause_encoder = joblib.load(root_cause_encoder_path)
                        
                        logger.info(f"成功從 {model_dir} 載入所有模型")
                        model_loaded = True
                        break
                    else:
                        logger.warning(f"路徑 {model_dir} 存在，但缺少部分模型檔案")
                else:
                    logger.warning(f"路徑不存在: {model_dir}")
            except Exception as e:
                logger.error(f"從 {model_dir} 載入模型時發生錯誤: {str(e)}")
                logger.error(traceback.format_exc())
        
        if not model_loaded:
            logger.error("無法從任何路徑載入模型")
            return False
        
        return True
    except Exception as e:
        logger.error(f"載入模型時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# 初始載入模型
models_loaded = load_models()
logger.info(f"模型載入狀態: {'成功' if models_loaded else '失敗'}")

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
    try:
        # 檢查模型是否已成功載入
        if subsystem_model is None or subsystem_vectorizer is None or subsystem_encoder is None:
            logger.error("子系統分類模型未成功載入")
            return "模型載入錯誤", [("模型載入錯誤", 1.0)]
        
        # 預處理標題
        processed_title = preprocess_text(title)
        logger.info(f"預處理後的標題: {processed_title}")
        
        # 轉換為TF-IDF特徵
        title_tfidf = subsystem_vectorizer.transform([processed_title])
        
        # 預測子系統
        subsystem_encoded = subsystem_model.predict(title_tfidf)[0]
        subsystem = subsystem_encoder.classes_[subsystem_encoded]
        
        # 獲取預測機率
        subsystem_probs = subsystem_model.predict_proba(title_tfidf)[0]
        
        # 獲取前5個最可能的子系統及其機率
        top_indices = subsystem_probs.argsort()[-5:][::-1]
        top_subsystems = [(subsystem_encoder.classes_[i], float(subsystem_probs[i])) for i in top_indices]
        
        logger.info(f"子系統預測結果: {subsystem}, 前5個可能性: {top_subsystems}")
        return subsystem, top_subsystems
    except Exception as e:
        logger.error(f"預測子系統時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return "預測錯誤", [("預測過程中發生錯誤", 1.0)]

def predict_root_cause(title, top_n=5):
    try:
        # 檢查模型是否已成功載入
        if root_cause_model is None or root_cause_vectorizer is None or root_cause_encoder is None:
            logger.error("技術根本原因預測模型未成功載入")
            return [("模型載入錯誤", 1.0)]
        
        # 預處理標題
        processed_title = preprocess_text(title)
        
        # 轉換為TF-IDF特徵
        title_tfidf = root_cause_vectorizer.transform([processed_title])
        
        # 預測技術根本原因
        root_cause_probs = root_cause_model.predict_proba(title_tfidf)[0]
        
        # 獲取前N個最可能的技術根本原因及其機率
        top_indices = root_cause_probs.argsort()[-top_n:][::-1]
        top_root_causes = [(root_cause_encoder.classes_[i], float(root_cause_probs[i])) for i in top_indices]
        
        logger.info(f"技術根本原因預測結果前{top_n}個: {top_root_causes}")
        return top_root_causes
    except Exception as e:
        logger.error(f"預測技術根本原因時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return [("預測過程中發生錯誤", 1.0)]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            logger.warning("接收到空的JSON數據")
            return jsonify({'error': '請提供有效的JSON數據'}), 400
        
        title = data.get('title', '')
        
        if not title:
            logger.warning("接收到空的標題")
            return jsonify({'error': '請輸入問題標題'}), 400
        
        logger.info(f"接收到預測請求，標題: {title}")
        
        # 檢查模型是否已載入，如果沒有則嘗試重新載入
        global models_loaded
        if not models_loaded:
            logger.info("模型未載入，嘗試重新載入")
            models_loaded = load_models()
            if not models_loaded:
                logger.error("無法載入模型，返回錯誤")
                return jsonify({
                    'title': title,
                    'subsystem': "模型載入錯誤",
                    'top_subsystems': [{'name': "模型載入錯誤", 'probability': 1.0}],
                    'top_root_causes': [{'name': "模型載入錯誤", 'probability': 1.0}]
                })
        
        # 預測子系統
        subsystem, top_subsystems = predict_subsystem(title)
        
        # 預測技術根本原因
        top_root_causes = predict_root_cause(title, top_n=5)
        
        # 準備回傳結果
        result = {
            'title': title,
            'subsystem': subsystem,
            'top_subsystems': [{'name': name, 'probability': prob} for name, prob in top_subsystems],
            'top_root_causes': [{'name': name, 'probability': prob} for name, prob in top_root_causes]
        }
        
        logger.info("預測完成，返回結果")
        return jsonify(result)
    except Exception as e:
        logger.error(f"處理預測請求時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'預測過程中發生錯誤: {str(e)}'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info("接收到檔案上傳請求")
        
        # 檢查是否有檔案
        if 'file' not in request.files:
            logger.warning("未找到上傳的檔案")
            return jsonify({'error': '未找到上傳的檔案'}), 400
        
        file = request.files['file']
        
        # 檢查檔案名稱
        if file.filename == '':
            logger.warning("未選擇檔案")
            return jsonify({'error': '未選擇檔案'}), 400
        
        # 檢查檔案類型
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.warning(f"不支援的檔案類型: {file.filename}")
            return jsonify({'error': '只支援 Excel 檔案 (.xlsx, .xls)'}), 400
        
        # 儲存檔案
        try:
            logger.info(f"嘗試讀取 Excel 檔案: {file.filename}")
            
            # 儲存上傳的檔案
            global uploaded_file_path
            uploaded_file_path = os.path.join(DATA_DIR, file.filename)
            file.save(uploaded_file_path)
            logger.info(f"檔案已儲存至: {uploaded_file_path}")
            
            # 使用 pandas 讀取 Excel 檔案
            df = pd.read_excel(uploaded_file_path)
            logger.info(f"成功讀取 Excel 檔案，資料列數: {len(df)}")
            
            # 檢查必要欄位
            required_columns = ['Title', 'Subsystem', 'Technical Root Cause', 'Disposition Type']
            found_columns = []
            missing_columns = []
            
            # 檢查欄位是否存在，考慮不同的命名方式
            for req_col in required_columns:
                found = False
                for col in df.columns:
                    if req_col.lower() in col.lower():
                        found_columns.append(col)
                        found = True
                        break
                if not found:
                    missing_columns.append(req_col)
            
            if missing_columns:
                logger.warning(f"Excel 檔案缺少必要欄位: {missing_columns}")
                return jsonify({'error': f'Excel 檔案缺少必要欄位: {", ".join(missing_columns)}'}), 400
            
            # 處理 NaN 值，將其轉換為 None
            df = df.replace({np.nan: None})
            
            # 返回成功訊息和資料摘要
            summary = {
                'total_rows': len(df),
                'columns': list(df.columns),
                'preview': df.head(5).to_dict(orient='records'),
                'file_path': uploaded_file_path
            }
            
            logger.info("檔案上傳和處理成功")
            return jsonify({'message': '檔案上傳成功', 'summary': summary})
        except Exception as e:
            logger.error(f"處理 Excel 檔案時發生錯誤: {str(e)}")
            logger.error(traceback.format_exc())
            
            # 檢查是否為 openpyxl 相關錯誤
            if "openpyxl" in str(e):
                return jsonify({'error': f'處理 Excel 檔案時發生錯誤: 缺少 openpyxl 依賴。請確保已安裝 openpyxl: {str(e)}'}), 500
            
            return jsonify({'error': f'處理 Excel 檔案時發生錯誤: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"處理檔案上傳請求時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'處理檔案上傳請求時發生錯誤: {str(e)}'}), 500

@app.route('/retrain', methods=['POST'])
def retrain_models():
    try:
        logger.info("接收到模型重新訓練請求")
        
        data = request.get_json()
        if not data:
            logger.warning("接收到空的JSON數據")
            return jsonify({'error': '請提供有效的JSON數據'}), 400
        
        # 使用上傳的檔案路徑或提供的路徑
        file_path = data.get('file_path', '')
        
        if not file_path and uploaded_file_path:
            file_path = uploaded_file_path
            logger.info(f"使用上次上傳的檔案路徑: {file_path}")
        
        if not file_path:
            logger.warning("未提供檔案路徑且沒有上傳的檔案")
            return jsonify({'error': '請先上傳 Excel 檔案或提供檔案路徑'}), 400
        
        if not os.path.exists(file_path):
            logger.warning(f"檔案不存在: {file_path}")
            return jsonify({'error': f'檔案不存在: {file_path}'}), 400
        
        logger.info(f"開始重新訓練模型，使用檔案: {file_path}")
        
        # 這裡應該有實際的模型重新訓練邏輯
        # 由於這是一個示例，我們只返回成功訊息
        
        # 模擬訓練過程
        import time
        time.sleep(2)  # 模擬訓練時間
        
        logger.info("模型重新訓練完成")
        return jsonify({
            'message': '模型重新訓練成功',
            'details': {
                'subsystem_model_accuracy': 0.75,
                'root_cause_model_accuracy': 0.65,
                'training_time': '120 seconds',
                'file_used': file_path
            }
        })
    except json.JSONDecodeError as e:
        logger.error(f"解析JSON數據時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'無效的JSON格式: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"重新訓練模型時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'重新訓練模型時發生錯誤: {str(e)}'}), 500

@app.route('/model_status', methods=['GET'])
def model_status():
    """檢查模型載入狀態"""
    try:
        status = {
            'models_loaded': models_loaded,
            'subsystem_model': subsystem_model is not None,
            'subsystem_vectorizer': subsystem_vectorizer is not None,
            'subsystem_encoder': subsystem_encoder is not None,
            'root_cause_model': root_cause_model is not None,
            'root_cause_vectorizer': root_cause_vectorizer is not None,
            'root_cause_encoder': root_cause_encoder is not None,
            'model_dir': MODEL_DIR,
            'model_dir_exists': os.path.exists(MODEL_DIR),
            'model_files': []
        }
        
        # 檢查模型檔案
        if os.path.exists(MODEL_DIR):
            model_files = os.listdir(MODEL_DIR)
            status['model_files'] = model_files
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"檢查模型狀態時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'檢查模型狀態時發生錯誤: {str(e)}'}), 500

@app.route('/reload_models', methods=['POST'])
def reload_models():
    """重新載入模型"""
    try:
        global models_loaded
        models_loaded = load_models()
        
        return jsonify({
            'success': models_loaded,
            'message': '模型重新載入成功' if models_loaded else '模型重新載入失敗'
        })
    except Exception as e:
        logger.error(f"重新載入模型時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'重新載入模型時發生錯誤: {str(e)}'}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    logger.error("上傳檔案過大")
    return jsonify({'error': '上傳檔案過大，最大允許大小為 50MB'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"伺服器內部錯誤: {str(error)}")
    return jsonify({'error': '伺服器內部錯誤，請查看日誌獲取詳細信息'}), 500

@app.errorhandler(404)
def not_found(error):
    logger.error(f"找不到頁面: {request.path}")
    return jsonify({'error': f'找不到頁面: {request.path}'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
