import requests
import time
import threading
from flask import Flask
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY"]

stats = {"run": 0}

def send(msg):
    print("📩 SENDING:", msg)
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
    except Exception as e:
        print("Telegram error:", e)

# 🔥 REAL PRICE TEST (no API dependency)
def fake_price(symbol):
    import random
    return round(1.10 + random.uniform(-0.01, 0.01), 5)

# 🔥 FORCE SIGNAL EVERY LOOP (DEBUG MODE)
def analyze(symbol):
    price = fake_price(symbol)
    print("📊 PRICE:", symbol, price)

    stats["run"] += 1

    if stats["run"] % 2 == 0:
        return "BUY", price
    else:
        return "SELL", price

def loop():
    print("🔁 SIGNAL LOOP STARTED")

    while True:

        for symbol in SYMBOLS:

            print("🔍 CHECK:", symbol)

            signal = analyze(symbol)

            print("📡 SIGNAL:", signal)

            if signal:
                direction, price = signal

                send(f"""
🔥 AI SIGNAL (DEBUG MODE)

Asset: {symbol}
Direction: {direction}
Price: {price}
Time: {datetime.now()}
""")

            time.sleep(5)

        time.sleep(10)

@app.route("/")
def home():
    return "BOT RUNNING"

if __name__ == "__main__":

    send("🚀 BOT STARTED SUCCESSFULLY")

    t = threading.Thread(target=loop, daemon=True)
    t.start()

    print("MAIN THREAD ACTIVE")

    app.run(host="0.0.0.0", port=10000)
