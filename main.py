import requests
import time
import threading
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

TIMEZONE = pytz.timezone("Asia/Kolkata")

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

stats = {"win": 0, "loss": 0, "total": 0}

# ---------- TELEGRAM ----------
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except:
        pass

# ---------- REAL PRICE ----------
def get_price(symbol):
    try:
        base = symbol[:3]
        quote = symbol[3:]
        url = f"https://api.exchangerate.host/latest?base={base}&symbols={quote}"
        r = requests.get(url, timeout=5).json()
        return float(r["rates"][quote])
    except:
        return None

# ---------- SIGNAL ENGINE ----------
def analyze(symbol):

    price = get_price(symbol)
    if not price:
        return None

    minute = datetime.now().minute
    score = 0

    if minute % 2 == 0:
        score += 1
    else:
        score -= 1

    if price > 1:
        score += 1
    else:
        score -= 1

    if score >= 2:
        return "BUY", price
    elif score <= -2:
        return "SELL", price

    return None

# ---------- RESULT CHECK ----------
def check_result(symbol, direction, entry):
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
        stats["win"] += 1
    else:
        stats["loss"] += 1

    send(f"""
📊 RESULT

Asset: {symbol}
Direction: {direction}

Entry: {entry}
Exit: {exit_price}

Result: {result}

WIN: {stats['win']}
LOSS: {stats['loss']}
TOTAL: {stats['total']}
""")

# ---------- LOOP ----------
def loop():

    while True:

        for symbol in SYMBOLS:

            signal = analyze(symbol)

            if not signal:
                continue

            direction, price = signal

            now = datetime.now(TIMEZONE)

            send(f"""
🔥 AI SIGNAL

Asset: {symbol}

Time: {now.strftime("%I:%M:%S %p")}

Direction: {direction}
Entry Price: {price}

TF: 1M / 2M / 5M
━━━━━━━━━━━━
""")

            threading.Thread(
                target=check_result,
                args=(symbol, direction, price)
            ).start()

            time.sleep(15)

        time.sleep(30)

# ---------- DASHBOARD ----------
@app.route("/")
def home():
    return f"""
    <h2>BOT LIVE</h2>
    <p>WIN: {stats['win']}</p>
    <p>LOSS: {stats['loss']}</p>
    <p>TOTAL: {stats['total']}</p>
    """

# ---------- START ----------
if __name__ == "__main__":
    send("BOT STARTED")
    threading.Thread(target=loop).start()
    app.run(host="0.0.0.0", port=10000)
