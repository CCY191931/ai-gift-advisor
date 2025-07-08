# gemini_proxy.py 的最終版本

# 1. 所有 import 都在最上面
import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import google.generativeai as genai
from dotenv import load_dotenv

# 2. 讀取 .env 檔案 (這只在本地開發時有效，在 Render 上會被忽略)
load_dotenv()

# 3. 建立 Flask App
app = Flask(__name__)

# 4. 設定 CORS，允許多個來源
#    這份列表讓您的線上前端和本地測試都能順利連接
origins_list = [
    "https://ai-gift-advisor-web.onrender.com", # Render 線上前端
    "http://127.0.0.1:5500",                   # VS Code Live Server 常用網址
    "http://localhost:8080"                     # 其他本地伺服器常用網址
]
CORS(app, resources={r"/api/*": {"origins": origins_list}})

# 5. 從環境變數安全地設定 Gemini API Key
model = None
try:
    # 這裡會先嘗試讀取 Render 上的環境變數，如果找不到，
    # load_dotenv() 會讓它接著讀取您本地 .env 檔案裡的變數
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        # 如果在任何地方都找不到金鑰，就拋出錯誤
        raise ValueError("錯誤：找不到名為 GEMINI_API_KEY 的環境變數。請在 Render 或 .env 檔案中設定。")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini API 金鑰設定成功，模型已準備就緒。")

except Exception as e:
    # 如果金鑰設定失敗或有其他問題，在啟動時就能從日誌看到
    print(f"FATAL: 初始化 Gemini 模型時發生錯誤 - {e}")
    traceback.print_exc()


# 6. 建立 API 路由 (Endpoint)
@app.route('/api/gemini', methods=['POST'])
def handle_gemini_request():
    # 檢查模型是否成功初始化
    if not model:
        return jsonify({"error": "Gemini 模型未成功初始化，請檢查伺服器啟動日誌。"}), 500
    
    # 處理前端發來的請求
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
             return jsonify({"error": "請求格式錯誤，缺少 'messages' 欄位。"}), 400

        messages = data.get('messages')
        
        # 使用 Google SDK 呼叫 Gemini
        response = model.generate_content(messages)
        
        # 回傳 Gemini 的文字回應
        return jsonify({"text": response.text})

    except Exception as e:
        # 捕捉處理請求時可能發生的任何錯誤
        print(f"Error during Gemini request: {traceback.format_exc()}")
        return jsonify({"error": "處理請求時發生內部錯誤。"}), 500

# 7. 在本地端直接執行此檔案時的啟動方式
#    (Render 會用 Gunicorn 啟動，所以不會執行到這一段)
if __name__ == '__main__':
    app.run(debug=True, port=3001)