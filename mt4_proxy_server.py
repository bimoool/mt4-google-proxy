from flask import Flask, request, jsonify
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route("/send", methods=["POST"])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON received"}), 400

    try:
        creds_json = os.environ["GSPREAD_CREDENTIALS"]
        creds_dict = json.loads(creds_json)

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        spreadsheet_id = "12IJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
        sheet = client.open_by_key(spreadsheet_id).worksheet("Forex")

        row = [
            data.get("account"),
            data.get("balance"),
            data.get("equity"),
            data.get("profit"),
            data.get("drawdown"),
            data.get("name"),
        ]
        sheet.append_row(row)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    return "MT4 Google Proxy is running.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
