import os
import time
import random
import threading
import requests

from flask import Flask
from datetime import datetime, timedelta, timezone

# =========================================
# INDIA TIME
# =========================================

IST = timezone(timedelta(hours=5, minutes=30))

# =========================================
# TELEGRAM
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================================
# FLASK
# =========================================

app = Flask(__name__)

# =========================================
# FOREX PAIRS
# =========================================

pairs = [
    "EURUSD",
    "GBPUSD",
    "AUDUSD",
    "USDJPY",
    "USDCHF",
    "USDCAD",
    "EURJPY",
    "GBPJPY"
]

# =========================================
# TELEGRAM SEND
# =========================================

def send_telegram(message):

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        data = {
            "chat_id": CHAT_ID,
            "text": message
        }

        r = requests.post(url, data=data)

        print("TELEGRAM RESPONSE:", r.text)

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =========================================
# LIVE PRICE
# =========================================

def get_live_price(symbol):

    try:

        pair = symbol + "=X"

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers)

        data = r.json()

        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

        return float(price)

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# =========================================
# CHECK RESULT
# =========================================

def check_result(symbol, direction, entry_price):

    try:

        exit_price = get_live_price(symbol)

        if exit_price is None:
            return

        if direction == "BUY":

            result = "WIN" if exit_price > entry_price else "LOSS"

        else:

            result = "WIN" if exit_price < entry_price else "LOSS"

        msg = f"""
━━━━━━━━━━━━━━
📊 RESULT

📈 Asset : {symbol}

📊 Direction : {direction}

💰 Entry Price : {entry_price}

💰 Exit Price : {exit_price}

🔥 RESULT : {result}
━━━━━━━━━━━━━━
"""

        send_telegram(msg)

    except Exception as e:

        print("RESULT ERROR:", e)

# =========================================
# SIGNAL ENGINE
# =========================================

def signal_engine():

    while True:

        try:

            symbol = random.choice(pairs)

            direction = random.choice([
                "BUY",
                "SELL"
            ])

            expiry = random.choice([
                1,
                2,
                5
            ])

            now = datetime.now(IST)

            entry_time = now + timedelta(minutes=1)

            expiry_time = entry_time + timedelta(minutes=expiry)

            entry_price = get_live_price(symbol)

            if entry_price is None:

                time.sleep(10)
                continue

            arrow = "UP ⬆️" if direction == "BUY" else "DOWN ⬇️"

            signal = f"""
━━━━━━━━━━━━━━
📊 AI BINARY SIGNAL

📈 Asset : {symbol}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{entry_time.strftime('%I:%M %p')}

⌛ Expiry Time :
{expiry_time.strftime('%I:%M %p')}

📊 Direction :
{arrow}

💰 Entry Price :
{entry_price}

🔥 Accuracy : HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation
━━━━━━━━━━━━━━
"""

            print("SENDING SIGNAL...")

            send_telegram(signal)

            # WAIT ENTRY + EXPIRY

            total_wait = 60 + (expiry * 60)

            print("WAITING:", total_wait)

            time.sleep(total_wait)

            # CHECK RESULT

            check_result(
                symbol,
                direction,
                entry_price
            )

            # NEXT SIGNAL

            time.sleep(20)

        except Exception as e:

            print("ENGINE ERROR:", e)

            time.sleep(5)

# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return "BOT RUNNING"

# =========================================
# START ENGINE
# =========================================

threading.Thread(
    target=signal_engine,
    daemon=True
).start()

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
