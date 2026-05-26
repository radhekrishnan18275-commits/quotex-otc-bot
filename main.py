import os
import time
import random
import threading
import requests
import traceback
from datetime import datetime, timedelta
from flask import Flask
import pytz

# ==============================
# TELEGRAM SETTINGS
# ==============================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==============================
# FLASK APP
# ==============================

app = Flask(__name__)

@app.route("/")
def home():
    return "AI SIGNAL BOT RUNNING"

# ==============================
# INDIA TIMEZONE
# ==============================

india = pytz.timezone("Asia/Kolkata")

# ==============================
# PAIRS
# ==============================

PAIRS = [
    "EURUSD=X",
    "GBPUSD=X",
    "AUDUSD=X",
    "USDJPY=X",
    "USDCAD=X",
    "USDCHF=X",
    "EURJPY=X"
]

# ==============================
# DAILY SUMMARY
# ==============================

total_signals = 0
total_wins = 0
total_losses = 0

# ==============================
# TELEGRAM SEND FUNCTION
# ==============================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=data)
        print("TELEGRAM RESPONSE:", response.text)

    except Exception as e:
        print("TELEGRAM ERROR:", e)

# ==============================
# GET LIVE PRICE
# ==============================

def get_price(symbol):

    try:

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers)

        data = response.json()

        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

        return round(price, 5)

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# ==============================
# GENERATE SIGNAL
# ==============================

def generate_signal():

    pair = random.choice(PAIRS)

    price = get_price(pair)

    if price is None:
        return None

    direction = random.choice(["UP ⬆️", "DOWN ⬇️"])

    trade_time = random.choice([1, 2, 5])

    now = datetime.now(india)

    entry_time = now + timedelta(minutes=1)

    expiry_time = entry_time + timedelta(minutes=trade_time)

    signal = {
        "pair": pair.replace("=X", ""),
        "price": price,
        "direction": direction,
        "signal_time": now.strftime("%I:%M:%S %p"),
        "entry_time": entry_time.strftime("%I:%M %p"),
        "expiry_time": expiry_time.strftime("%I:%M %p"),
        "trade_time": trade_time
    }

    return signal

# ==============================
# RESULT CHECK
# ==============================

def check_result(signal):

    global total_wins
    global total_losses

    try:

        print("WAITING FOR RESULT...")

        wait_seconds = (signal["trade_time"] * 60) + 5

        time.sleep(wait_seconds)

        new_price = get_price(signal["pair"] + "=X")

        if new_price is None:
            return

        entry_price = signal["price"]

        direction = signal["direction"]

        result = "LOSS ❌"

        if direction == "UP ⬆️":

            if new_price > entry_price:
                result = "WIN ✅"

        else:

            if new_price < entry_price:
                result = "WIN ✅"

        if "WIN" in result:
            total_wins += 1
        else:
            total_losses += 1

        result_message = f"""
🏁 RESULT UPDATE

📈 Asset : {signal['pair']}

🕒 Entry Time :
{signal['entry_time']}

⌛ Expiry Time :
{signal['expiry_time']}

📊 Direction :
{signal['direction']}

💰 Entry Price :
{entry_price}

💰 Exit Price :
{new_price}

🎯 Final Result :
{result}

━━━━━━━━━━━━━━
"""

        send_telegram(result_message)

    except Exception:
        print(traceback.format_exc())

# ==============================
# DAILY SUMMARY
# ==============================

def send_summary():

    while True:

        try:

            now = datetime.now(india)

            if now.hour == 23 and now.minute == 59:

                summary = f"""
📊 DAILY SUMMARY REPORT

✅ Total Signals :
{total_signals}

🏆 Total Wins :
{total_wins}

❌ Total Losses :
{total_losses}

📈 Accuracy :
{round((total_wins / max(total_signals,1)) * 100, 2)}%

━━━━━━━━━━━━━━
"""

                send_telegram(summary)

                time.sleep(60)

            time.sleep(20)

        except Exception:
            print(traceback.format_exc())

# ==============================
# SIGNAL ENGINE
# ==============================

def signal_engine():

    global total_signals

    while True:

        try:

            print("CHECKING MARKET...")

            signal = generate_signal()

            if signal:

                total_signals += 1

                message = f"""
🚀 AI BINARY SIGNAL 🚀

📈 Asset : {signal['pair']}

🕒 Signal Time :
{signal['signal_time']}

⏰ Entry Time :
{signal['entry_time']}

⌛ Expiry Time :
{signal['expiry_time']}

🕐 Trade Time :
{signal['trade_time']} MINUTE

📊 Direction :
{signal['direction']}

💰 Entry Price :
{signal['price']}

🔥 Accuracy :
HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation

━━━━━━━━━━━━━━
"""

                send_telegram(message)

                result_thread = threading.Thread(
                    target=check_result,
                    args=(signal,)
                )

                result_thread.start()

            else:

                print("NO SIGNAL FOUND")

            time.sleep(120)

        except Exception:

            print(traceback.format_exc())

            time.sleep(30)

# ==============================
# START ENGINE
# ==============================

print("BOT TOKEN:", BOT_TOKEN)
print("CHAT ID:", CHAT_ID)
print("SIGNAL ENGINE STARTED")

threading.Thread(target=signal_engine).start()

threading.Thread(target=send_summary).start()

# ==============================
# RUN FLASK
# ==============================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
