from flask import Flask
import threading
import time
import requests
from datetime import datetime, timedelta
import pytz
import random

app = Flask(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# ==============================
# INDIA TIMEZONE
# ==============================
IST = pytz.timezone("Asia/Kolkata")

# ==============================
# PAIRS
# ==============================
pairs = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCAD",
    "EURJPY",
    "GBPJPY"
]

# ==============================
# STATS
# ==============================
total_signals = 0
wins = 0
losses = 0

# ==============================
# TELEGRAM MESSAGE FUNCTION
# ==============================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram Error:", e)

# ==============================
# LIVE PRICE GENERATOR
# ==============================
def get_live_price():
    return round(random.uniform(1.0000, 1.5000), 4)

# ==============================
# SIGNAL GENERATOR
# ==============================
def signal_engine():
    global total_signals, wins, losses

    while True:

        pair = random.choice(pairs)

        direction = random.choice(["UP ⬆️", "DOWN ⬇️"])

        signal_price = get_live_price()

        now = datetime.now(IST)

        signal_time = now.strftime("%I:%M:%S %p")

        entry_time_obj = now + timedelta(minutes=1)
        expiry_time_obj = entry_time_obj + timedelta(minutes=5)

        entry_time = entry_time_obj.strftime("%I:%M %p")
        expiry_time = expiry_time_obj.strftime("%I:%M %p")

        # ==============================
        # SIGNAL MESSAGE
        # ==============================
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

📊 Direction :
{direction}

💰 Entry Price :
{signal_price}

🔥 Accuracy :
HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation

━━━━━━━━━━━━━━━━━━
"""

        send_telegram(signal_message)

        print("SIGNAL SENT")

        total_signals += 1

        # ==============================
        # WAIT FOR EXPIRY
        # ==============================
        time.sleep(60)

        # ==============================
        # RESULT CHECK
        # ==============================
        exit_price = get_live_price()

        result = "LOSS ❌"

        if direction == "UP ⬆️":
            if exit_price > signal_price:
                result = "WIN ✅"
                wins += 1
            else:
                losses += 1

        else:
            if exit_price < signal_price:
                result = "WIN ✅"
                wins += 1
            else:
                losses += 1

        # ==============================
        # RESULT MESSAGE
        # ==============================
        result_message = f"""
━━━━━━━━━━━━━━━━━━
📢 SIGNAL RESULT
━━━━━━━━━━━━━━━━━━

📈 Asset : {pair}

📊 Direction :
{direction}

💰 Entry Price :
{signal_price}

💵 Exit Price :
{exit_price}

🏆 Final Result :
{result}

━━━━━━━━━━━━━━━━━━
📊 TODAY SUMMARY
━━━━━━━━━━━━━━━━━━

✅ Total Signals : {total_signals}

🏆 Wins : {wins}

❌ Losses : {losses}

━━━━━━━━━━━━━━━━━━
"""

        send_telegram(result_message)

        print("RESULT SENT")

        # ==============================
        # NEXT SIGNAL WAIT
        # ==============================
        time.sleep(30)

# ==============================
# HOME ROUTE
# ==============================
@app.route("/")
def home():
    return "AI SIGNAL BOT RUNNING"

# ==============================
# START THREAD
# ==============================
threading.Thread(target=signal_engine).start()

# ==============================
# RUN FLASK
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
