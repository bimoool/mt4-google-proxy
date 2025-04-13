import os
import json
import logging
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация Google Sheets
sheet = None
init_error = None
try:
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS not set")
    
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    SPREADSHEET_ID = "12IJZgUKeCjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
    SHEET_NAME = "Forex"
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    logger.info("Google Sheet инициализирован")
except Exception as e:
    init_error = str(e)
    logger.error(f"Ошибка инициализации: {init_error}")

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "running",
        "sheet_initialized": sheet is not None,
        "init_error": init_error
    })

@app.route("/send", methods=["POST"])
def receive_data():
    logger.info("mt4_proxy_server:Запрос получен: %s", request.get_data(as_text=True))
    if sheet is None:
        return jsonify({"error": "Google Sheet не инициализирован"}), 500

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Неверный JSON"}), 400

        row = [
            str(data.get("account", "")),
            str(data.get("balance", "")),
            str(data.get("equity", "")),
            str(data.get("profit", "")),
            str(data.get("drawdown", "")),
            str(data.get("name", ""))
        ]

        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info("mt4_proxy_server:Данные успешно добавлены: %s", row)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error("mt4_proxy_server:Ошибка при обработке запроса: %s", str(e))
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
