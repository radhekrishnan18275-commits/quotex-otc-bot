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
# TELEGRAM SETTINGS
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT TOKEN:", BOT_TOKEN)
print("CHAT ID:", CHAT_ID)

# =========================================
# FLASK
# =========================================

app = Flask(__name__)

# =========================================
# PAIRS
# =========================================

pairs = [
    "EURUSD",
    "GBPUSD",
    "AUDUSD",
    "USDJPY"
]

# =========================================
# TELEGRAM MESSAGE
# =========================================

def send_telegram(message):

    try:

        print("SENDING TELEGRAM...")

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message
        }

        response = requests.post(url, data=payload)

        print("TELEGRAM STATUS:", response.status_code)
        print("TELEGRAM RESPONSE:", response.text)

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =========================================
# GET LIVE PRICE
# =========================================

def get_live_price(symbol):

    try:

        pair = symbol + "=X"

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        print("PRICE STATUS:", response.status_code)

        data = response.json()

        print("PRICE DATA:", data)

        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

        print(symbol, "PRICE:", price)

        return float(price)

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# =========================================
# RESULT CHECK
# =========================================

def check_result(symbol, direction, entry_price):

    try:

        print("CHECKING RESULT...")

        exit_price = get_live_price(symbol)

        if exit_price is None:

            print("EXIT PRICE FAILED")
            return

        if direction == "BUY":

            result = "WIN" if exit_price > entry_price else "LOSS"

        else:

            result = "WIN" if exit_price < entry_price else "LOSS"

        result_message = f"""
RESULT

PAIR: {symbol}

DIRECTION: {direction}

ENTRY: {entry_price}

EXIT: {exit_price}

FINAL RESULT: {result}
"""

        send_telegram(result_message)

    except Exception as e:

        print("RESULT ERROR:", e)

# =========================================
# SIGNAL ENGINE
# =========================================

def signal_engine():

    print("SIGNAL ENGINE STARTED")

    while True:

        try:

            symbol = random.choice(pairs)

            direction = random.choice([
                "BUY",
                "SELL"
            ])

            expiry = 1

            print("SELECTED PAIR:", symbol)

            entry_price = get_live_price(symbol)

            if entry_price is None:

                print("ENTRY PRICE FAILED")

                time.sleep(10)

                continue

            now = datetime.now(IST)

            entry_time = now + timedelta(minutes=1)

            expiry_time = entry_time + timedelta(minutes=expiry)

            arrow = "UP ⬆️" if direction == "BUY" else "DOWN ⬇️"

            signal_message = f"""
AI SIGNAL

PAIR: {symbol}

TIME: {now.strftime('%I:%M:%S %p')}

ENTRY: {entry_time.strftime('%I:%M %p')}

EXPIRY: {expiry_time.strftime('%I:%M %p')}

DIRECTION: {arrow}

PRICE: {entry_price}
"""

            send_telegram(signal_message)

            print("SIGNAL SENT SUCCESS")

            # WAIT

            total_wait = 60 + (expiry * 60)

            print("WAITING", total_wait, "SECONDS")

            time.sleep(total_wait)

            # RESULT

            check_result(
                symbol,
                direction,
                entry_price
            )

            print("NEXT SIGNAL IN 20 SEC")

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
# START THREAD
# =========================================

threading.Thread(
    target=signal_engine,
    daemon=True
).start()

# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
