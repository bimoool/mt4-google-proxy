import os
import json
import logging
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mt4_proxy_server")

app = Flask(__name__)

# Глобальные переменные
sheet = None
init_error = None

# Инициализация Google Sheets
try:
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS переменная окружения не установлена")

    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    client = gspread.authorize(creds)

    sheet_id = os.getenv("SPREADSHEET_ID")
    if not sheet_id:
        raise ValueError("SPREADSHEET_ID переменная окружения не установлена")

    sheet = client.open_by_key(sheet_id).worksheet("Forex")
    logger.info("✅ Google Sheet успешно инициализирован")

except Exception as e:
    init_error = str(e)
    logger.error("❌ Ошибка при инициализации Google Sheets: %s", init_error)


@app.route("/", methods=["GET"])
def index():
    status = {
        "status": "running",
        "sheet_initialized": sheet is not None,
    }
    if init_error:
        status["init_error"] = init_error
    return jsonify(status)


@app.route("/send", methods=["POST"])
def receive_data():
    global sheet
    if not sheet:
        return jsonify({"error": "Google Sheet не инициализирован", "init_error": init_error}), 500

    try:
        raw_data = request.get_data().decode("utf-8")
        logger.info("📥 RAW BODY: %s", raw_data)

        data = json.loads(raw_data)
        logger.info("✅ JSON получен: %s", data)

        required_fields = ["account", "balance", "equity", "profit", "drawdown", "name"]
        values = []
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing field: {field}")
            values.append(str(data[field]))

        sheet.append_row(values)
        logger.info("📤 Данные успешно добавлены: %s", values)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error("❌ Ошибка при обработке запроса: %s", str(e))
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
