from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# ✅ 1. Авторизация по ключу из переменной окружения
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

json_str = os.environ.get("GSPREAD_CREDENTIALS")
if not json_str:
    raise Exception("⛔ Переменная окружения GSPREAD_CREDENTIALS не установлена!")
creds_dict = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ✅ 2. Подключение к Google Spreadsheet и нужному листу
SPREADSHEET_ID = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"  # <-- заменяется при необходимости
SHEET_NAME = "Forex"  # Название листа в таблице
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# ✅ 3. Обработка входящего запроса от MT4
@app.route('/send', methods=['POST'])
def receive_mt4_data():
    try:
        data = request.get_json(force=True)
        print("✅ Данные получены от MT4:", data)

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
        return "OK", 200

    except Exception as e:
        print("⛔ Ошибка при получении или записи данных:", str(e))
        return f"Ошибка: {str(e)}", 500

# ✅ 4. Flask запускается на порту из окружения (важно для Render)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render задаёт этот порт!
    app.run(host="0.0.0.0", port=port)
