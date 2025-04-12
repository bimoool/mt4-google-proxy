from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("beitler-150312-c9446af5d76a.json", scope)
client = gspread.authorize(creds)

# Используем конкретный документ и лист "Forex"
spreadsheet_id = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
sheet = client.open_by_key(spreadsheet_id).worksheet("Forex")

@app.route('/send', methods=['POST'])
def receive_mt4_data():
    data = request.get_json()
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
    app.run(port=5000)