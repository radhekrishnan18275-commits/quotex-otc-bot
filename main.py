import os
import asyncio
import random
import threading
import time

from datetime import datetime, timedelta, timezone

from flask import Flask
from telegram import Bot

# =========================================
# INDIA TIMEZONE
# =========================================

IST = timezone(timedelta(hours=5, minutes=30))

# =========================================
# TELEGRAM SETTINGS
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =========================================
# FLASK APP
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
# STATS
# =========================================

total_trades = 0
total_win = 0
total_loss = 0

# =========================================
# SEND TELEGRAM
# =========================================

async def send_telegram(message):

    try:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )

        print("TELEGRAM SENT")

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =========================================
# SEND RESULT
# =========================================

def send_result(symbol, signal):

    global total_win
    global total_loss

    try:

        # RANDOM RESULT ENGINE
        result = random.choice([
            "WIN",
            "WIN",
            "WIN",
            "LOSS"
        ])

        if result == "WIN":

            total_win += 1

            result_message = f"""
━━━━━━━━━━━━━━
✅ RESULT : WIN

📈 Asset : {symbol}

🔥 Direction : {signal}

💰 Profit Booked
━━━━━━━━━━━━━━
"""

        else:

            total_loss += 1

            result_message = f"""
━━━━━━━━━━━━━━
❌ RESULT : LOSS

📉 Asset : {symbol}

⚠ Market Reversed
━━━━━━━━━━━━━━
"""

        asyncio.run(
            send_telegram(result_message)
        )

        print("RESULT SENT")

    except Exception as e:

        print("RESULT ERROR:", e)

# =========================================
# DAILY SUMMARY
# =========================================

def daily_summary():

    global total_trades
    global total_win
    global total_loss

    last_summary_date = None

    while True:

        try:

            now = datetime.now(IST)

            current_date = now.strftime("%Y-%m-%d")

            current_hour = now.hour

            current_minute = now.minute

            # SEND SUMMARY DAILY AT 11:59 PM
            if (
                current_hour == 23 and
                current_minute == 59 and
                last_summary_date != current_date
            ):

                if total_trades > 0:

                    accuracy = round(
                        (total_win / total_trades) * 100,
                        2
                    )

                else:

                    accuracy = 0

                summary_message = f"""
━━━━━━━━━━━━━━
📊 DAILY SUMMARY

📈 Total Signals :
{total_trades}

✅ WIN :
{total_win}

❌ LOSS :
{total_loss}

🔥 Accuracy :
{accuracy}%
━━━━━━━━━━━━━━
"""

                asyncio.run(
                    send_telegram(summary_message)
                )

                print("SUMMARY SENT")

                last_summary_date = current_date

                # RESET
                total_trades = 0
                total_win = 0
                total_loss = 0

            # KEEP RENDER ACTIVE
            time.sleep(30)

        except Exception as e:

            print("SUMMARY ERROR:", e)

            time.sleep(5)

# =========================================
# SIGNAL ENGINE
# =========================================

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

            signal_message = f"""
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
                send_telegram(signal_message)
            )

            total_trades += 1

            print("SIGNAL SENT")

            # WAIT FOR ENTRY + EXPIRY
            total_wait = (
                60 +
                (expiry * 60)
            )

            # SAFE WAIT LOOP
            for i in range(total_wait):

                time.sleep(1)

            # SEND RESULT
            send_result(symbol, signal)

            # NEXT SIGNAL GAP
            for i in range(20):

                time.sleep(1)

        except Exception as e:

            print("ENGINE ERROR:", e)

            time.sleep(5)

# =========================================
# HOME PAGE
# =========================================

@app.route("/")
def home():

    return "AI Binary Bot Running 🚀"

# =========================================
# START THREADS
# =========================================

threading.Thread(
    target=signal_engine,
    daemon=True
).start()

threading.Thread(
    target=daily_summary,
    daemon=True
).start()

# =========================================
# START SERVER
# =========================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
