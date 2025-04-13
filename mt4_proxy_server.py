import os
import json
import logging
from flask import Flask, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

# Логгирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds_json = os.getenv("GOOGLE_CREDENTIALS")
if not creds_json:
    raise Exception("GOOGLE_CREDENTIALS env var not set")

creds_dict = json.loads(creds_json)
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# !!! ВНИМАНИЕ: проверь это имя
sheet = client.open_by_key("12IJZgUKeCjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc").worksheet("Forex")

@app.route("/")
def index():
    return "pong", 200

@app.route("/send", methods=["POST"])
def receive_data():
    try:
        logger.info("Request received: %s", request.get_data(as_text=True))
        data = request.get_json()
        if not data:
            logger.warning("No JSON in request")
            return jsonify({"error": "No JSON payload"}), 400

        row = [
            str(data.get("account")),
            str(data.get("balance")),
            str(data.get("equity")),
            str(data.get("profit")),
            str(data.get("drawdown")),
            str(data.get("name"))
        ]
        logger.info("Appending row to sheet: %s", row)
        sheet.append_row(row)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error("Error while handling request: %s", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
