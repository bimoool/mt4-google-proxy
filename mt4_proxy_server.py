from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# Настройки Google API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

json_str = os.environ.get("GSPREAD_CREDENTIALS")
if not json_str:
    raise Exception("GSPREAD_CREDENTIALS env var not set")

creds_dict = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Открываем таблицу и лист
spreadsheet_id = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
sheet = client.open_by_key(spreadsheet_id).worksheet("Forex")

@app.route("/send", methods=["POST"])
def receive():
    data = request.get_json()
    print("✅ Data received:", data)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        data.get("account"),
        data.get("balance"),
        data.get("equity"),
        data.get("profit"),
        data.get("drawdown"),
        data.get("name"),
        timestamp
    ]
    sheet.append_row(row)
    return "OK", 200

# 🧙🏾‍♂️ Production запуск через waitress
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)
