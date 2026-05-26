import requests
import time
import threading
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

# ================= CONFIG =================
BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

TIMEZONE = pytz.timezone("Asia/Kolkata")

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]

stats = {"win": 0, "loss": 0, "total": 0}

# ================= TELEGRAM =================
def send(msg):
    try:
        print("📩 TELEGRAM:", msg)
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        print("Telegram error:", e)

# ================= REAL PRICE =================
def get_price(symbol):
    try:
        sym = symbol.lower()
        url = f"https://stooq.com/q/l/?s={sym}&f=sd2t2ohlc&h&e=json"
        r = requests.get(url, timeout=5).json()
        return float(r["symbols"][0]["close"])
    except Exception as e:
        print("PRICE ERROR:", symbol, e)
        return None

# ================= SIGNAL ENGINE =================
def analyze(symbol):

    price = get_price(symbol)

    if not price:
        return None

    print("📊 PRICE OK:", symbol, price)

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

    print("📈 SCORE:", symbol, score)

    if score >= 2:
        return "BUY", price
    elif score <= -2:
        return "SELL", price

    return None

# ================= RESULT CHECK =================
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

# ================= SIGNAL LOOP =================
def loop():

    print("🔁 SIGNAL LOOP STARTED")

    while True:

        try:
            for symbol in SYMBOLS:

                print("🔍 Checking:", symbol)

                signal = analyze(symbol)

                print("📡 SIGNAL:", symbol, signal)

                if not signal:
                    continue

                direction, price = signal

                now = datetime.now(TIMEZONE)

                send(f"""
🔥 AI SIGNAL

Asset: {symbol}
Time: {now.strftime("%I:%M:%S %p")}

Direction: {direction}
Price: {price}
""")

                threading.Thread(
                    target=check_result,
                    args=(symbol, direction, price)
                ).start()

                time.sleep(10)

            time.sleep(20)

        except Exception as e:
            print("LOOP ERROR:", e)

# ================= DASHBOARD =================
@app.route("/")
def home():
    return "BOT RUNNING OK"

# ================= START =================
if __name__ == "__main__":

    send("🚀 BOT STARTED SUCCESSFULLY")

    t = threading.Thread(target=loop, daemon=True)
    t.start()

    print("🚀 MAIN THREAD RUNNING")

    app.run(host="0.0.0.0", port=10000)
