from flask import Flask, request, jsonify
from datetime import datetime
import json
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key="PUT_YOUR_API_KEY_HERE")

DB_FILE = "devices.json"
MONTHLY_LIMIT = 1000

# تحميل الداتا
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# API رئيسي
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    device_id = data.get("device_id")
    question = data.get("question")

    db = load_db()

    if device_id not in db:
        db[device_id] = {
            "month": datetime.now().month,
            "count": 0
        }

    # reset كل شهر
    if db[device_id]["month"] != datetime.now().month:
        db[device_id]["month"] = datetime.now().month
        db[device_id]["count"] = 0

    # تحقق من الحد
    if db[device_id]["count"] >= MONTHLY_LIMIT:
        return jsonify({"answer": "تم استهلاك الباقة الشهرية"})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "رد باللهجة المصرية"},
                {"role": "user", "content": question}
            ]
        )

        db[device_id]["count"] += 1
        save_db(db)

        return jsonify({
            "answer": response.choices[0].message.content,
            "usage": db[device_id]["count"]
        })

    except Exception as e:
        print(e)
        return jsonify({"answer": "في مشكلة في السيرفر"})
    
# تشغيل السيرفر
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)