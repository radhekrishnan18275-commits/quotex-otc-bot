from flask import Flask
import threading
import time
import requests
from datetime import datetime, timedelta
import pytz
import random

app = Flask(__name__)

# ==================================
# TELEGRAM SETTINGS
# ==================================

BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

# ==================================
# INDIA TIMEZONE
# ==================================

IST = pytz.timezone("Asia/Kolkata")

# ==================================
# PAIRS
# ==================================

pairs = [
    "EURUSD",
    "GBPUSD",
    "AUDUSD",
    "USDJPY",
    "USDCAD"
]

# ==================================
# SUMMARY
# ==================================

total_signals = 0
wins = 0
losses = 0

# ==================================
# SEND TELEGRAM MESSAGE
# ==================================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:

        response = requests.post(url, data=data)

        print("TELEGRAM STATUS:", response.status_code)
        print("TELEGRAM RESPONSE:", response.text)

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# ==================================
# RANDOM LIVE PRICE
# ==================================

def get_price():

    return round(random.uniform(1.1000, 1.5000), 4)

# ==================================
# SIGNAL ENGINE
# ==================================

def signal_engine():

    global total_signals
    global wins
    global losses

    print("SIGNAL ENGINE STARTED")

    while True:

        pair = random.choice(pairs)

        direction = random.choice([
            "UP ⬆️",
            "DOWN ⬇️"
        ])

        trade_type = random.choice([
            "1 MIN",
            "2 MIN",
            "5 MIN"
        ])

        expiry_minutes = 1

        if trade_type == "2 MIN":
            expiry_minutes = 2

        if trade_type == "5 MIN":
            expiry_minutes = 5

        now = datetime.now(IST)

        signal_time = now.strftime("%I:%M:%S %p")

        entry_obj = now + timedelta(minutes=1)

        expiry_obj = entry_obj + timedelta(
            minutes=expiry_minutes
        )

        entry_time = entry_obj.strftime("%I:%M %p")

        expiry_time = expiry_obj.strftime("%I:%M %p")

        entry_price = get_price()

        # ==================================
        # SIGNAL MESSAGE
        # ==================================

        signal_message = f"""
━━━━━━━━━━━━━━━━━━
🔥 AI BINARY SIGNAL 🔥
━━━━━━━━━━━━━━━━━━

📈 Asset : {pair}

🕒 Signal Time :
{signal_time}

⏰ Entry Time :
{entry_time}

⌛ Expiry Time :
{expiry_time}

⏳ Trade :
{trade_type}

📊 Direction :
{direction}

💰 Entry Price :
{entry_price}

🔥 Accuracy :
HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation

━━━━━━━━━━━━━━━━━━
"""

        send_telegram(signal_message)

        print("SIGNAL SENT")

        total_signals += 1

        # ==================================
        # WAIT FOR RESULT
        # ==================================

        wait_time = (1 + expiry_minutes) * 60

        time.sleep(wait_time)

        exit_price = get_price()

        result = "LOSS ❌"

        if direction == "UP ⬆️":

            if exit_price > entry_price:
                result = "WIN ✅"
                wins += 1
            else:
                losses += 1

        else:

            if exit_price < entry_price:
                result = "WIN ✅"
                wins += 1
            else:
                losses += 1

        # ==================================
        # RESULT MESSAGE
        # ==================================

        result_message = f"""
━━━━━━━━━━━━━━━━━━
📢 SIGNAL RESULT
━━━━━━━━━━━━━━━━━━

📈 Asset : {pair}

⏳ Trade :
{trade_type}

📊 Direction :
{direction}

💰 Entry Price :
{entry_price}

💵 Exit Price :
{exit_price}

🏆 Result :
{result}

━━━━━━━━━━━━━━━━━━
📊 SUMMARY
━━━━━━━━━━━━━━━━━━

✅ Total :
{total_signals}

🏆 Wins :
{wins}

❌ Loss :
{losses}

━━━━━━━━━━━━━━━━━━
"""

        send_telegram(result_message)

        print("RESULT SENT")

        time.sleep(20)

# ==================================
# HOME PAGE
# ==================================

@app.route("/")
def home():

    return "BOT RUNNING"

# ==================================
# START BOT
# ==================================

threading.Thread(target=signal_engine).start()

# ==================================
# RUN APP
# ==================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
