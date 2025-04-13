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

# === Google Sheets ===
sheet = None
init_error = None

try:
    creds_json = os.getenv("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS переменная окружения не установлена")

    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)

    client = gspread.authorize(creds)
    sheet = client.open_by_key("12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc").worksheet("Forex")
    logger.info("Google Sheet успешно инициализирован")
except Exception as e:
    init_error = str(e)
    logger.error("Ошибка при инициализации Google Sheets: %s", init_error)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "running",
        "sheet_initialized": sheet is not None,
        "init_error": init_error
    })

@app.route("/send", methods=["POST"])
def send():
    logger.info("Запрос получен: %s", request.get_data(as_text=True))
    if sheet is None:
        return jsonify({"error": "Google Sheet не инициализирован", "init_error": init_error}), 500

    try:
        data = request.get_json(force=True, silent=False)
        logger.info("Данные JSON: %s", data)

        row = [
            str(data.get("account", "")),
            str(data.get("balance", "")),
            str(data.get("equity", "")),
            str(data.get("profit", "")),
            str(data.get("drawdown", "")),
            str(data.get("name", ""))
        ]

        if not any(row):
            return jsonify({"error": "Пустые данные"}), 400

        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info("Данные успешно добавлены: %s", row)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error("Ошибка при обработке запроса: %s", str(e))
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
