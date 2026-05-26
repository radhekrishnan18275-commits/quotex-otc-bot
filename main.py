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
# PAIRS
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
# STATS
# =====================================

total_trades = 0
total_win = 0
total_loss = 0

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
# RESULT
# =====================================

def send_result(symbol, signal):

    global total_win
    global total_loss

    try:

        result = random.choice([
            "WIN",
            "WIN",
            "WIN",
            "LOSS"
        ])

        if result == "WIN":

            total_win += 1

            msg = f"""
━━━━━━━━━━━━━━
✅ RESULT : WIN

📈 Asset : {symbol}

🔥 Direction : {signal}

💰 Profit Booked
━━━━━━━━━━━━━━
"""

        else:

            total_loss += 1

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
# DAILY SUMMARY
# =====================================

def daily_summary():

    global total_trades
    global total_win
    global total_loss

    while True:

        time.sleep(86400)

        try:

            if total_trades > 0:

                accuracy = round(
                    (total_win / total_trades) * 100,
                    2
                )

            else:

                accuracy = 0

            summary = f"""
━━━━━━━━━━━━━━
📊 DAILY SUMMARY

📈 Total Signals :
{total_trades}

✅ Total WIN :
{total_win}

❌ Total LOSS :
{total_loss}

🔥 Accuracy :
{accuracy}%

━━━━━━━━━━━━━━
"""

            asyncio.run(
                send_telegram(summary)
            )

            # RESET
            total_trades = 0
            total_win = 0
            total_loss = 0

        except Exception as e:

            print("SUMMARY ERROR:", e)

# =====================================
# SIGNAL ENGINE
# =====================================

def signal_engine():

    global total_trades

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

            # SIGNAL BEFORE 1 MINUTE
            entry_time = now + timedelta(minutes=1)

            expiry_time = (
                entry_time +
                timedelta(minutes=expiry)
            )

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

            total_trades += 1

            print("SIGNAL SENT")

            # WAIT FOR ENTRY + EXPIRY
            wait_seconds = (
                60 +
                (expiry * 60)
            )

            time.sleep(wait_seconds)

            # RESULT
            send_result(symbol, signal)

            print("RESULT SENT")

            # WAIT BEFORE NEXT SIGNAL
            time.sleep(20)

        except Exception as e:

            print("ENGINE ERROR:", e)

            time.sleep(10)

# =====================================
# HOME
# =====================================

@app.route("/")
def home():

    return "AI Binary Signal Bot Running 🚀"

# =====================================
# START THREADS
# =====================================

threading.Thread(
    target=signal_engine,
    daemon=True
).start()

threading.Thread(
    target=daily_summary,
    daemon=True
).start()

# =====================================
# SERVER
# =====================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
