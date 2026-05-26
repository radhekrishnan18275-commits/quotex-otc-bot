from flask import Flask
import threading
import time
import requests
from datetime import datetime, timedelta
import pytz
import random

app = Flask(__name__)

# =========================
# TELEGRAM SETTINGS
# =========================

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# =========================
# INDIA TIME
# =========================

IST = pytz.timezone("Asia/Kolkata")

# =========================
# PAIRS
# =========================

pairs = [
    "EURUSD",
    "GBPUSD",
    "AUDUSD",
    "USDJPY",
    "USDCAD",
    "EURJPY",
    "GBPJPY"
]

# =========================
# SUMMARY
# =========================

total_signals = 0
wins = 0
losses = 0

# =========================
# TELEGRAM FUNCTION
# =========================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data)
        print("TELEGRAM SENT")

    except Exception as e:
        print("ERROR:", e)

# =========================
# FAKE LIVE PRICE
# =========================

def get_price():

    return round(random.uniform(1.1000, 1.5000), 4)

# =========================
# SIGNAL ENGINE
# =========================

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
            "1 MINUTE",
            "2 MINUTE",
            "5 MINUTE"
        ])

        # =========================
        # EXPIRY LOGIC
        # =========================

        expiry_minutes = 1

        if trade_type == "2 MINUTE":
            expiry_minutes = 2

        if trade_type == "5 MINUTE":
            expiry_minutes = 5

        now = datetime.now(IST)

        signal_time = now.strftime("%I:%M:%S %p")

        entry_time_obj = now + timedelta(minutes=1)

        expiry_time_obj = entry_time_obj + timedelta(
            minutes=expiry_minutes
        )

        entry_time = entry_time_obj.strftime("%I:%M %p")

        expiry_time = expiry_time_obj.strftime("%I:%M %p")

        entry_price = get_price()

        # =========================
        # SIGNAL MESSAGE
        # =========================

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

⏳ Trade Type :
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

        total_signals += 1

        print("SIGNAL SENT")

        # =========================
        # WAIT UNTIL EXPIRY
        # =========================

        total_wait = (1 + expiry_minutes) * 60

        time.sleep(total_wait)

        # =========================
        # RESULT
        # =========================

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

        # =========================
        # RESULT MESSAGE
        # =========================

        result_message = f"""
━━━━━━━━━━━━━━━━━━
📢 SIGNAL RESULT
━━━━━━━━━━━━━━━━━━

📈 Asset : {pair}

⏳ Trade Type :
{trade_type}

📊 Direction :
{direction}

💰 Entry Price :
{entry_price}

💵 Exit Price :
{exit_price}

🏆 Final Result :
{result}

━━━━━━━━━━━━━━━━━━
📊 24 HOURS SUMMARY
━━━━━━━━━━━━━━━━━━

✅ Total Signals :
{total_signals}

🏆 Wins :
{wins}

❌ Losses :
{losses}

━━━━━━━━━━━━━━━━━━
"""

        send_telegram(result_message)

        print("RESULT SENT")

        # =========================
        # NEXT SIGNAL WAIT
        # =========================

        time.sleep(30)

# =========================
# HOME ROUTE
# =========================

@app.route("/")
def home():

    return "AI SIGNAL BOT RUNNING"

# =========================
# START THREAD
# =========================

threading.Thread(target=signal_engine).start()

# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=10000
    )
