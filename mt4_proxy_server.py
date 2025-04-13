import os
import json
from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def send():
    try:
        data = request.get_json(force=True)

        # Авторизация через переменную окружения
        creds_json = os.environ.get("GSPREAD_CREDENTIALS")
        if not creds_json:
            raise Exception("GSPREAD_CREDENTIALS env var not set")

        creds_dict = json.loads(creds_json)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        # Открываем таблицу по ID и лист "Forex"
        spreadsheet_id = "12lJZgUKeCjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
        sheet = client.open_by_key(spreadsheet_id).worksheet("Forex")

        # Записываем строку
        sheet.append_row([
            data.get("account"),
            data.get("balance"),
            data.get("equity"),
            data.get("profit"),
            data.get("drawdown"),
            data.get("name"),
        ])

        return "OK", 200

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
