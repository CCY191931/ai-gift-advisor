# gemini_proxy.py 的「最終偵錯版」

import os
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

origins_list = [
    "https://ai-gift-advisor-web.onrender.com",
    "http://127.0.0.1:5500",
    "http://localhost:8080"
]
CORS(app, resources={r"/api/*": {"origins": origins_list}})

model = None
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("錯誤：找不到名為 GEMINI_API_KEY 的環境變數。")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini API 金鑰設定成功，模型已準備就緒。")
except Exception as e:
    print(f"FATAL: 初始化 Gemini 模型時發生錯誤 - {e}")
    traceback.print_exc()


# ★★★ 新增的偵錯專用 API 路由 ★★★
@app.route('/api/debug-key', methods=['GET'])
def debug_key():
    print("正在執行 /api/debug-key 路由...")
    key_to_check = os.environ.get("GEMINI_API_KEY", "未設定 (Not Set)")
    
    if len(key_to_check) > 10:
        response_data = {
            "message": "成功讀取到環境變數",
            "key_head": key_to_check[:5] + "...",
            "key_tail": "..." + key_to_check[-5:],
            "key_length": len(key_to_check)
        }
    else:
        response_data = {
            "message": "讀取到的環境變數有問題",
            "key_value": key_to_check
        }
    
    print(f"偵錯路由回傳的資料: {response_data}")
    return jsonify(response_data)


@app.route('/api/gemini', methods=['POST'])
def handle_gemini_request():
    if not model:
        return jsonify({"error": "Gemini 模型未成功初始化，請檢查伺服器啟動日誌。"}), 500
    
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({"error": "請求格式錯誤，缺少 'messages' 欄位。"}), 400

        messages = data.get('messages')
        response = model.generate_content(messages)
        return jsonify({"text": response.text})

    except Exception as e:
        print(f"Error during Gemini request: {traceback.format_exc()}")
        return jsonify({"error": "處理請求時發生內部錯誤。"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3001)