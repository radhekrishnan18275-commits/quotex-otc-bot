from flask import Flask, request
import requests
import pytz
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

BOT_TOKEN = "YOUR_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

india = pytz.timezone("Asia/Kolkata")

wins = 0
losses = 0
total = 0

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def evaluate(symbol, direction, entry):

    global wins, losses, total

    import time
    time.sleep(60)  # 1 min expiry default

    # fake exit simulation replaced with real webhook price tracking later
    import random
    result = random.choice(["WIN", "LOSS"])

    total += 1

    if result == "WIN":
        wins += 1
    else:
        losses += 1

    send(f"""
📊 RESULT

Asset: {symbol}
Result: {result}

Wins: {wins}
Losses: {losses}
Total: {total}
""")

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    symbol = data["symbol"]
    signal = data["signal"]
    price = data["price"]

    now = datetime.now(india)

    direction = "BUY" if "BUY" in signal else "SELL"

    entry_time = now + timedelta(minutes=1)

    msg = f"""
📢 AI SIGNAL

Asset: {symbol}
Signal: {signal}

Entry: {entry_time.strftime("%I:%M %p")}
Price: {price}

Strategy: EMA + RSI + MACD
"""

    send(msg)

    threading.Thread(target=evaluate, args=(symbol, direction, price)).start()

    return "OK", 200

@app.route("/")
def home():
    return "LIVE BOT RUNNING"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
