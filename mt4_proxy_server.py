from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# ✅ Логируем каждый входящий запрос
@app.before_request
def log_request_info():
    print(f"📥 Получен запрос: method={request.method}, path={request.path}")

# 🔐 Настройка авторизации Google API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

json_str = os.environ.get("GSPREAD_CREDENTIALS")
if not json_str:
    raise Exception("Переменная окружения GSPREAD_CREDENTIALS не установлена!")
creds_dict = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📘 Доступ к нужной таблице и листу
SPREADSHEET_ID = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
SHEET_NAME = "Forex"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# 🚦 Проверка: GET /
@app.route("/", methods=["GET"])
def index():
    return "🧙🏾 MT4 Proxy is alive", 200

# 📬 Приём POST-запросов от MT4
@app.route("/send", methods=["POST"])
def receive_mt4_data():
    try:
        print("🔥 [POST] /send — Запрос получен")
        data = request.get_json(force=True)
        print("📦 Полученные данные:", data)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            data.get("account"),
            data.get("balance"),
            data.get("equity"),
            data.get("profit"),
            data.get("drawdown"),
            timestamp
        ]
        print("📋 Строка для записи:", row)

        sheet.append_row(row)
        print("✅ УСПЕШНО: данные записаны")

        return jsonify({"status": "success", "message": "Данные записаны"}), 200

    except Exception as e:
        print("⛔ Ошибка при обработке запроса:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# 🚀 Запуск сервера на порту Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Flask-сервер запущен на порту {port}")
    app.run(host="0.0.0.0", port=port)
