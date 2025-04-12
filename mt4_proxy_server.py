from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# Настройка авторизации с Google API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Получение ключей из переменной окружения
json_str = os.environ.get("GSPREAD_CREDENTIALS")
if not json_str:
    raise Exception("Переменная окружения GSPREAD_CREDENTIALS не установлена!")
creds_dict = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Открываем таблицу и лист
SPREADSHEET_ID = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
SHEET_NAME = "Forex"
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# 🔧 Роут для проверки сервера
@app.route("/", methods=["GET"])
def index():
    return "🧙🏾 MT4 Proxy is alive", 200

# 📬 Роут для приёма данных от MT4
@app.route("/send", methods=["POST"])
def receive_mt4_data():
    try:
        data = request.get_json(force=True)
        print("✅ Данные от MT4:", data)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            data.get("account"),
            data.get("balance"),
            data.get("equity"),
            data.get("profit"),
            data.get("drawdown"),
            timestamp
        ]
        sheet.append_row(row)

        return jsonify({"status": "success", "message": "Данные записаны"}), 200

    except Exception as e:
        print("⛔ Ошибка:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

# 🚀 Запуск сервера на порту от Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
