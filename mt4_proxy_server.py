from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ MT4 Proxy is live."

@app.route("/send", methods=["POST"])
def send_stats():
    try:
        # Принудительно парсим JSON
        data = request.get_json(force=True)

        if not data:
            print("⚠️ JSON не распознан или пуст.")
            return jsonify({"error": "No JSON received"}), 400

        # Логируем входящие данные
        print("✅ Получены данные:", data)

        # Здесь можно сохранить в Google Таблицу или БД

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Ошибка обработки запроса:", str(e))
        return jsonify({"error": str(e)}), 500

# Запуск при локальной отладке (не используется на Render)
#if __name__ == "__main__":
 #   app.run(host="0.0.0.0", port=10000)
