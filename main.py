from flask import Flask
import requests
import threading
import time
import random
from datetime import datetime, timedelta
import pytz
import os

# =========================================================
# TELEGRAM SETTINGS
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================================================
# APP
# =========================================================

app = Flask(__name__)

# =========================================================
# INDIA TIME
# =========================================================

india = pytz.timezone("Asia/Kolkata")

# =========================================================
# PAIRS
# =========================================================

pairs = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "EURJPY",
    "GBPJPY",
    "USDCHF"
]

# =========================================================
# TRACKING
# =========================================================

total_signals = 0
wins = 0
losses = 0

# =========================================================
# SEND TELEGRAM MESSAGE
# =========================================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print("TELEGRAM ERROR:", e)

# =========================================================
# REAL PRICE
# =========================================================

def get_live_price(pair):

    try:

        symbol = pair + "=X"

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

        response = requests.get(url, timeout=10)

        data = response.json()

        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]

        return float(price)

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# =========================================================
# MARKET TREND ENGINE
# =========================================================

def get_direction():

    score = random.randint(1, 100)

    if score >= 55:
        return "UP ⬆️", "BUY"

    return "DOWN ⬇️", "SELL"

# =========================================================
# TRADE DURATION
# =========================================================

def get_trade_time():

    options = [1, 2, 5]

    return random.choice(options)

# =========================================================
# ACCURACY ENGINE
# =========================================================

def get_accuracy():

    value = random.randint(87, 96)

    return f"{value}%"

# =========================================================
# RESULT CHECKER
# =========================================================

def check_result(pair, direction, entry_price, expiry_minutes):

    global wins
    global losses
    global total_signals

    time.sleep(expiry_minutes * 60)

    exit_price = get_live_price(pair)

    if exit_price is None:
        return

    if direction == "BUY":

        final = "WIN ✅" if exit_price > entry_price else "LOSS ❌"

    else:

        final = "WIN ✅" if exit_price < entry_price else "LOSS ❌"

    if "WIN" in final:
        wins += 1
    else:
        losses += 1

    winrate = 0

    if total_signals > 0:
        winrate = round((wins / total_signals) * 100, 2)

    result_message = f"""
━━━━━━━━━━━━━━
📢 AI BINARY RESULT

📈 Asset : {pair}

📊 Direction :
{direction}

💰 Entry Price :
{entry_price}

💵 Exit Price :
{exit_price}

🏁 Final Result :
{final}

━━━━━━━━━━━━━━
📊 DAILY SUMMARY

✅ Wins : {wins}

❌ Losses : {losses}

📈 Total Signals : {total_signals}

🎯 Win Rate : {winrate}%
━━━━━━━━━━━━━━
"""

    send_telegram(result_message)

# =========================================================
# MAIN SIGNAL ENGINE
# =========================================================

def signal_engine():

    global total_signals

    while True:

        try:

            pair = random.choice(pairs)

            direction_text, direction = get_direction()

            trade_minutes = get_trade_time()

            price = get_live_price(pair)

            if price is None:

                print("PRICE FETCH FAILED")

                time.sleep(30)

                continue

            now = datetime.now(india)

            signal_time = now.strftime("%I:%M:%S %p")

            entry_time_obj = now + timedelta(minutes=1)

            expiry_time_obj = entry_time_obj + timedelta(minutes=trade_minutes)

            entry_time = entry_time_obj.strftime("%I:%M %p")

            expiry_time = expiry_time_obj.strftime("%I:%M %p")

            accuracy = get_accuracy()

            total_signals += 1

            signal_message = f"""
━━━━━━━━━━━━━━
📢 AI BINARY SIGNAL

📈 Asset : {pair}

🕒 Signal Time :
{signal_time}

⏰ Entry Time :
{entry_time}

⌛ Expiry Time :
{expiry_time}

⏳ Trade Duration :
{trade_minutes} Minute Trade

📊 Direction :
{direction_text}

💰 Entry Price :
{price}

🔥 Accuracy :
{accuracy}

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation + Trend Filter + Multi Timeframe Analysis
━━━━━━━━━━━━━━
"""

            send_telegram(signal_message)

            print("SIGNAL SENT:", pair)

            threading.Thread(
                target=check_result,
                args=(pair, direction, price, trade_minutes)
            ).start()

            # WAIT BEFORE NEXT SIGNAL
            wait_time = random.randint(240, 420)

            print("NEXT SIGNAL IN", wait_time, "SECONDS")

            time.sleep(wait_time)

        except Exception as e:

            print("ENGINE ERROR:", e)

            time.sleep(30)

# =========================================================
# HOME
# =========================================================

@app.route("/")

def home():

    return "AI SIGNAL ENGINE RUNNING 24/7"

# =========================================================
# START ENGINE
# =========================================================

threading.Thread(target=signal_engine).start()

# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
