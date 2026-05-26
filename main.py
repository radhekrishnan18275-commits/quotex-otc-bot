import requests
import time
import pytz
from datetime import datetime, timedelta
import pandas as pd
import ta
import threading
from flask import Flask

app = Flask(__name__)

# ================= CONFIG =================
BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

TIMEZONE = pytz.timezone("Asia/Kolkata")

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

stats = {
    "wins": 0,
    "losses": 0,
    "total": 0
}

# ================= TELEGRAM SAFE SEND =================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for i in range(3):  # retry system
        try:
            r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
            if r.status_code == 200:
                return True
        except:
            time.sleep(2)
    print("Telegram failed:", msg)
    return False

# ================= REAL MARKET DATA (FOREX via free API proxy) =================
def get_price(symbol):
    try:
        url = f"https://api.exchangerate.host/latest?base={symbol[:3]}&symbols={symbol[3:]}"
        r = requests.get(url, timeout=5).json()
        return float(r["rates"][symbol[3:]])
    except:
        return None

# ================= SIGNAL ENGINE =================
def analyze(symbol):

    price = get_price(symbol)
    if not price:
        return None

    # simulated market micro-trend using time cycles (stable replacement for fake candles)
    now = datetime.utcnow().minute

    score = 0

    if now % 2 == 0:
        score += 1
    else:
        score -= 1

    if price % 2 > 1:
        score += 1
    else:
        score -= 1

    if score >= 2:
        return "BUY", price, score
    elif score <= -2:
        return "SELL", price, score
    else:
        return None

# ================= RESULT ENGINE =================
def result_checker(symbol, direction, entry):

    time.sleep(60)

    exit_price = get_price(symbol)
    if not exit_price:
        return

    stats["total"] += 1

    if direction == "BUY":
        result = "WIN" if exit_price > entry else "LOSS"
    else:
        result = "WIN" if exit_price < entry else "LOSS"

    if result == "WIN":
        stats["wins"] += 1
    else:
        stats["losses"] += 1

    send(f"""
📊 RESULT

Asset: {symbol}
Direction: {direction}

Entry: {entry}
Exit: {exit_price}

Result: {result}

Wins: {stats["wins"]}
Losses: {stats["losses"]}
Total: {stats["total"]}
""")

# ================= SIGNAL LOOP (24/7 CORE ENGINE) =================
def signal_loop():

    while True:

        try:
            for symbol in SYMBOLS:

                signal = analyze(symbol)

                if not signal:
                    continue

                direction, price, score = signal

                now = datetime.now(TIMEZONE)

                send(f"""
📊 AI PRO SIGNAL

Asset: {symbol}

Time: {now.strftime("%I:%M:%S %p")}

Direction: {direction}
Entry Price: {price}
Score: {score}

TF: 1M / 2M / 5M Strategy
━━━━━━━━━━━━━━
""")

                threading.Thread(
                    target=result_checker,
                    args=(symbol, direction, price)
                ).start()

                time.sleep(10)  # avoid spam

        except Exception as e:
            send(f"❌ BOT ERROR: {e}")

        time.sleep(20)

# ================= DASHBOARD =================
@app.route("/")
def home():

    wr = 0
    if stats["total"] > 0:
        wr = (stats["wins"] / stats["total"]) * 100

    return f"""
    <h2>🚀 HEDGE FUND PRO v4 LIVE</h2>
    <p>Wins: {stats['wins']}</p>
    <p>Losses: {stats['losses']}</p>
    <p>Total: {stats['total']}</p>
    <p>Win Rate: {wr:.2f}%</p>
    """

# ================= START =================
if __name__ == "__main__":

    threading.Thread(target=signal_loop).start()

    app.run(host="0.0.0.0", port=10000)
