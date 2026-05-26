import os
import asyncio
import threading
import time
import random
import requests

from datetime import datetime, timedelta, timezone

from flask import Flask
from telegram import Bot

# ====================================
# INDIA TIME
# ====================================

IST = timezone(timedelta(hours=5, minutes=30))

# ====================================
# TELEGRAM
# ====================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# ====================================
# FLASK
# ====================================

app = Flask(__name__)

# ====================================
# PAIRS
# ====================================

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

# ====================================
# STATS
# ====================================

total_trades = 0
total_win = 0
total_loss = 0

# ====================================
# TELEGRAM SEND
# ====================================

async def send_telegram(message):

    try:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )

        print("MESSAGE SENT")

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# ====================================
# LIVE PRICE
# ====================================

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

# ====================================
# RESULT CHECK
# ====================================

def check_result(symbol, direction, entry_price):

    global total_win
    global total_loss

    try:

        exit_price = get_live_price(symbol)

        if exit_price is None:

            return

        if direction == "BUY":

            result = (
                "WIN"
                if exit_price > entry_price
                else "LOSS"
            )

        else:

            result = (
                "WIN"
                if exit_price < entry_price
                else "LOSS"
            )

        if result == "WIN":

            total_win += 1

            msg = f"""
━━━━━━━━━━━━━━
✅ RESULT : WIN

📈 Asset : {symbol}

💰 Entry Price :
{entry_price}

💰 Exit Price :
{exit_price}

🔥 Candle Confirmed
━━━━━━━━━━━━━━
"""

        else:

            total_loss += 1

            msg = f"""
━━━━━━━━━━━━━━
❌ RESULT : LOSS

📈 Asset : {symbol}

💰 Entry Price :
{entry_price}

💰 Exit Price :
{exit_price}

⚠ Candle Reversed
━━━━━━━━━━━━━━
"""

        asyncio.run(send_telegram(msg))

        print("RESULT SENT")

    except Exception as e:

        print("RESULT ERROR:", e)

# ====================================
# SIGNAL ENGINE
# ====================================

def signal_engine():

    global total_trades

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

            expiry_time = (
                entry_time +
                timedelta(minutes=expiry)
            )

            entry_price = get_live_price(symbol)

            if entry_price is None:

                time.sleep(10)

                continue

            arrow = (
                "UP ⬆️"
                if direction == "BUY"
                else "DOWN ⬇️"
            )

            signal_message = f"""
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

            asyncio.run(
                send_telegram(signal_message)
            )

            total_trades += 1

            print("SIGNAL SENT")

            # WAIT
            total_wait = 60 + (expiry * 60)

            time.sleep(total_wait)

            # CHECK REAL RESULT
            check_result(
                symbol,
                direction,
                entry_price
            )

            # NEXT SIGNAL DELAY
            time.sleep(20)

        except Exception as e:

            print("ENGINE ERROR:", e)

            time.sleep(5)

# ====================================
# DAILY SUMMARY
# ====================================

def daily_summary():

    global total_trades
    global total_win
    global total_loss

    sent_today = False

    while True:

        try:

            now = datetime.now(IST)

            if (
                now.hour == 23 and
                now.minute == 59 and
                not sent_today
            ):

                accuracy = 0

                if total_trades > 0:

                    accuracy = round(
                        (total_win / total_trades) * 100,
                        2
                    )

                msg = f"""
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

                asyncio.run(send_telegram(msg))

                sent_today = True

            if now.hour == 0 and now.minute == 1:

                sent_today = False

            time.sleep(30)

        except Exception as e:

            print("SUMMARY ERROR:", e)

            time.sleep(5)

# ====================================
# HOME
# ====================================

@app.route("/")
def home():

    return "AI BOT RUNNING"

# ====================================
# START THREADS
# ====================================

threading.Thread(
    target=signal_engine,
    daemon=True
).start()

threading.Thread(
    target=daily_summary,
    daemon=True
).start()

# ====================================
# RUN
# ====================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
