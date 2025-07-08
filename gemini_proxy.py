import traceback
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://ai-gift-advisor-web.onrender.com"}})
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS 
import time

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = "AIzaSyA-PIfNpixKKKjHn3oWJeQk05R049cm6-U"

@app.route('/api/gemini', methods=['POST'])
def gemini():
    data = request.get_json()
    messages = data.get('messages', [])
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "\n".join(messages)}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 256,
            "temperature": 0.7
        }
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload)
            if resp.status_code == 429:
                if attempt < max_retries - 1:
                    time.sleep(5)  # 等待 5 秒再重試
                    continue
                else:
                    return jsonify({"error": "API 流量超過限制，請稍後再試"}), 429
            resp.raise_for_status()
            result = resp.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "（無回應）")
            return jsonify({"text": text})
        except Exception as e:
            if attempt == max_retries - 1:
                traceback.print_exc()
                return jsonify({"error": str(e)}), 500
            else:
                time.sleep(5)

if __name__ == '__main__':
    app.run(port=3001, debug=True)
