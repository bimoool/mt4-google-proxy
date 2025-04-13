from flask import Flask, request, jsonify
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload received"}), 400

        creds_json = os.getenv("GSPREAD_CREDENTIALS")
        if not creds_json:
            raise Exception("GSPREAD_CREDENTIALS env var not set")

        creds_dict = json.loads(creds_json)

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(credentials)

        spreadsheet_id = "12IJZgUKeCjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
        sheet = client.open_by_key(spreadsheet_id).worksheet("Forex")

        row = [
            str(data.get("account")),
            str(data.get("balance")),
            str(data.get("equity")),
            str(data.get("profit")),
            str(data.get("drawdown")),
            str(data.get("name")),
        ]

        sheet.append_row(row)
        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "MT4 Proxy Server is running", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
