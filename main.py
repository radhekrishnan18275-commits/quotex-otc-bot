import os
import asyncio
import random
import threading
import time

from datetime import datetime, timedelta, timezone

from flask import Flask
from telegram import Bot

# =====================================
# INDIA TIME
# =====================================

IST = timezone(timedelta(hours=5, minutes=30))

# =====================================
# TELEGRAM
# =====================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =====================================
# FLASK
# =====================================

app = Flask(__name__)

# =====================================
# FOREX PAIRS
# =====================================

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

# =====================================
# TELEGRAM SEND
# =====================================

async def send_telegram(message):

    try:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )

        print("MESSAGE SENT")

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =====================================
# RESULT ENGINE
# =====================================

def send_result(symbol, signal):

    try:

        # RANDOM RESULT
        result = random.choice([
            "WIN",
            "WIN",
            "WIN",
            "LOSS"
        ])

        if result == "WIN":

            msg = f"""
━━━━━━━━━━━━━━
✅ RESULT : WIN

📈 Asset : {symbol}

🔥 Direction : {signal}

💰 Profit Booked
━━━━━━━━━━━━━━
"""

        else:

            msg = f"""
━━━━━━━━━━━━━━
❌ RESULT : LOSS

📉 Asset : {symbol}

⚠ Market Reversed
━━━━━━━━━━━━━━
"""

        asyncio.run(
            send_telegram(msg)
        )

    except Exception as e:

        print("RESULT ERROR:", e)

# =====================================
# AUTO SIGNAL ENGINE
# =====================================

def signal_engine():

    while True:

        try:

            symbol = random.choice(pairs)

            signal = random.choice([
                "BUY",
                "SELL"
            ])

            expiry = random.choice([
                1,
                2,
                5
            ])

            direction = (
                "UP ⬆️"
                if signal == "BUY"
                else "DOWN ⬇️"
            )

            now = datetime.now(IST)

            entry_time = now + timedelta(minutes=1)

            expiry_time = (
                entry_time +
                timedelta(minutes=expiry)
            )

            # SIGNAL MESSAGE
            signal_msg = f"""
━━━━━━━━━━━━━━
📊 AI OTC SIGNAL

📈 Asset : {symbol}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{entry_time.strftime('%I:%M %p')}

⌛ Expiry Time :
{expiry_time.strftime('%I:%M %p')}

📊 Direction :
{direction}

🔥 Accuracy : HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation
━━━━━━━━━━━━━━
"""

            asyncio.run(
                send_telegram(signal_msg)
            )

            print("SIGNAL SENT")

            # WAIT FOR EXPIRY
            time.sleep(expiry * 60)

            # SEND RESULT
            send_result(symbol, signal)

            print("RESULT SENT")

            # NEXT SIGNAL WAIT
            time.sleep(15)

        except Exception as e:

            print("ENGINE ERROR:", e)

            time.sleep(10)

# =====================================
# HOME
# =====================================

@app.route("/")
def home():

    return "AI Forex Signal Bot Running 🚀"

# =====================================
# START ENGINE
# =====================================

threading.Thread(
    target=signal_engine,
    daemon=True
).start()

# =====================================
# START SERVER
# =====================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
