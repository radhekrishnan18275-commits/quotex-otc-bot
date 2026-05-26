import os
import time
from datetime import datetime, timedelta
import requests

# =========================
# CONFIG (USE ENV VARS)
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram send function
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)


# =========================
# SIGNAL FORMATTER
# =========================
def format_signal(asset, direction, price, expiry_min):

    now = datetime.now()
    entry_time = now + timedelta(minutes=1)
    expiry_time = now + timedelta(minutes=expiry_min)

    arrow = "⬆️" if direction == "BUY" else "⬇️"

    message = f"""
━━━━━━━━━━━━━━━━━━
🔥 AI BINARY SIGNAL 🔥
━━━━━━━━━━━━━━━━━━

📈 Asset : {asset}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{entry_time.strftime('%I:%M %p')}

⌛ Expiry Time :
{expiry_time.strftime('%I:%M %p')}

⏳ Trade :
{expiry_min} MIN

📊 Direction :
{direction} {arrow}

💰 Entry Price :
{price}

🔥 Accuracy :
HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation

━━━━━━━━━━━━━━━━━━
📊 SIGNAL STATUS : ACTIVE
━━━━━━━━━━━━━━━━━━
"""

    return message


# =========================
# DEMO SIGNAL GENERATOR
# (Replace with your AI logic)
# =========================
def generate_signal():
    # Example dummy signal (replace with your real bot logic)
    return {
        "asset": "USDJPY",
        "direction": "BUY",
        "price": 1.09083
    }


# =========================
# MAIN LOOP (24/7 BOT)
# =========================
def run_bot():

    print("🚀 BOT STARTED")

    while True:

        try:
            signal = generate_signal()

            for expiry in [1, 2, 5]:

                msg = format_signal(
                    asset=signal["asset"],
                    direction=signal["direction"],
                    price=signal["price"],
                    expiry_min=expiry
                )

                print(msg)  # debug
                send_telegram(msg)

                time.sleep(2)

            # wait before next cycle
            time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)


# =========================
# START
# =========================
if __name__ == "__main__":
    run_bot()
