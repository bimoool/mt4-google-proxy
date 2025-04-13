FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "mt4_proxy_server:app", "--bind", "0.0.0.0:8080"]
