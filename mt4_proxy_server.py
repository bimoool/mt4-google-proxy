from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime

app = Flask(__name__)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

json_str = os.environ["GSPREAD_CREDENTIALS"]
creds_dict = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

spreadsheet_id = "1zLJZgUKecjmGH4BJSIbfDhpDdWM5kpD_TeXzunAu5Tc"
sheet = client.open_by_key(spreadsheet_id).worksheet("Forex")

@app.route('/send', methods=['POST'])
def receive_mt4_data():
    data = request.get_json()

    print("Data received:", data)

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
    return "OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
