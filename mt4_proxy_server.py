from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# 🌐 Настройка доступа к Google API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# 🔐 Получение JSON-ключа из переменной окружения
json_str = os.environ.get("GSPREAD_CREDENTIALS")
if not json_str:
    raise Exception("Переменная окружения GSPREAD_CREDENTIALS не установлена!")
creds_dict = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 📘 Подключение к таблице и листу
SPREADSHEET_ID = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
SHEET_NAME = "Forex"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# 🚦 Проверка, что сервер работает
@app.route("/", methods=["GET"])
def index():
    return "🧙🏾 MT4 Proxy is alive", 200

# 📬 Приём данных от MT4
@app.route("/send", methods=["POST"])
def receive_mt4_data():
    try:
        print("🔥 [POST] /send пришёл")
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
        print("📋 Строка для вставки в таблицу:", row)

        sheet.append_row(row)
        print("✅ УСПЕХ: Данные записаны в Google Sheets")

        return jsonify({"status": "success", "message": "Данные записаны"}), 200

    except Exception as e:
        print("⛔ ОШИБКА:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# 🚀 Запуск на нужном порту (Render требует PORT из переменных окружения)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Запуск Flask-сервера на порту {port}")
    app.run(host="0.0.0.0", port=port)
