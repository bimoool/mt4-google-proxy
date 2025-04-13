import os
import json
import logging
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация Google Sheets
try:
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise Exception("GOOGLE_CREDENTIALS env var not set")
    
    creds_dict = json.loads(creds_json)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    # Открытие таблицы по ID и имени листа
    SPREADSHEET_ID = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
    SHEET_NAME = "Forex"
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
except Exception as e:
    logger.error(f"Ошибка при инициализации Google Sheets: {e}")
    sheet = None

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "running",
        "sheet_initialized": sheet is not None,
        "init_error": init_error
    }), 200

@app.route("/send", methods=["POST"])
def receive_data():
    logger.info("Запрос получен: %s", request.get_data(as_text=True))
    try:
        if sheet is None:
            raise Exception("Google Sheet не инициализирован")

        data = request.get_json()
        if not data:
            return jsonify({"error": "Нет JSON-данных"}), 400

        row = [
            str(data.get("account", "")),
            str(data.get("balance", "")),
            str(data.get("equity", "")),
            str(data.get("profit", "")),
            str(data.get("drawdown", "")),
            str(data.get("name", "")),
        ]

        sheet.append_row(row)
        logger.info("Данные успешно добавлены: %s", row)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
