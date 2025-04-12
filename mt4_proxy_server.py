from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

app = Flask(__name__)

# Настройки доступа к Google API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Загрузка ключей из переменной окружения GSPREAD_CREDENTIALS
json_str = os.environ.get("GSPREAD_CREDENTIALS")
if not json_str:
    raise Exception("Переменная окружения GSPREAD_CREDENTIALS не установлена")
creds_dict = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Открываем нужный Google Spreadsheet и лист "Forex"
spreadsheet_id = "12lJZgUKecjmGH4BJSIbfDhpDdwMSkpD-IeXzunAu5Tc"
sheet = client.open_by_key(spreadsheet_id).worksheet("Forex")

@app.route('/send', methods=['POST'])
def receive_mt4_data():
    data = request.get_json()
    # Отладочная печать: выводим полученные данные в консоль
    print("Data received:", data)
    return "OK"
    
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
    return "OK", 200

if __name__ == '__main__':
    # Используем порт из переменной окружения PORT, если он указан, иначе 5000
    port = int(os.environ.get("PORT", 5010))
    app.run(host="0.0.0.0", port=port)
