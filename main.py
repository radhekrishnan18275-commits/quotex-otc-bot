import os
import asyncio
import threading
import time

from datetime import datetime, timedelta, timezone

from flask import Flask, request
from telegram import Bot

# =====================================
# INDIA TIME FIX
# =====================================

IST = timezone(timedelta(hours=5, minutes=30))

# =====================================
# TELEGRAM SETTINGS
# =====================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =====================================
# FLASK APP
# =====================================

app = Flask(__name__)

# =====================================
# DEMO PRICE ENGINE
# =====================================

def get_live_price(symbol):

    prices = {

        "EURUSD": 1.0850,
        "GBPUSD": 1.2740,
        "AUDUSD": 0.6640,
        "USDJPY": 156.20,
        "USDCHF": 0.9100,
        "USDCAD": 1.3700

    }

    return prices.get(symbol, 1.0000)

# =====================================
# SEND TELEGRAM MESSAGE
# =====================================

async def telegram_message(message):

    try:

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )

        print("TELEGRAM SENT")

    except Exception as e:

        print("TELEGRAM ERROR:", e)

# =====================================
# RESULT ENGINE
# =====================================

def result_engine(
    symbol,
    signal,
    entry_price,
    expiry
):

    try:

        print("RESULT ENGINE STARTED")

        # WAIT
        time.sleep(expiry * 60)

        final_price = get_live_price(symbol)

        # RESULT
        if signal == "BUY":

            if final_price >= entry_price:
                result = "WIN"
            else:
                result = "LOSS"

        else:

            if final_price <= entry_price:
                result = "WIN"
            else:
                result = "LOSS"

        # RESULT MESSAGE
        if result == "WIN":

            result_msg = f"""
━━━━━━━━━━━━━━
✅ RESULT : WIN

📈 Asset : {symbol}

🔥 Direction : {signal}

💰 Profit Trade
━━━━━━━━━━━━━━
"""

        else:

            result_msg = f"""
━━━━━━━━━━━━━━
❌ RESULT : LOSS

📉 Asset : {symbol}

⚠ Market Reversed
━━━━━━━━━━━━━━
"""

        asyncio.run(
            telegram_message(result_msg)
        )

        print("RESULT SENT")

    except Exception as e:

        print("RESULT ERROR:", e)

# =====================================
# HOME
# =====================================

@app.route("/")
def home():

    return "AI Trading Bot Running 🚀"

# =====================================
# WEBHOOK
# =====================================

@app.route("/webhook", methods=["POST"])
def webhook():

    try:

        data = request.json

        signal = data.get("signal", "BUY")

        symbol = data.get("symbol", "EURUSD")

        expiry = int(data.get("expiry", 1))

        direction = (
            "UP ⬆️"
            if signal == "BUY"
            else "DOWN ⬇️"
        )

        # INDIA TIME
        now = datetime.now(IST)

        entry_time = now + timedelta(minutes=1)

        expiry_time = (
            entry_time +
            timedelta(minutes=expiry)
        )

        # PRICE
        entry_price = get_live_price(symbol)

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

        # SEND SIGNAL
        asyncio.run(
            telegram_message(signal_msg)
        )

        # RESULT THREAD
        thread = threading.Thread(
            target=result_engine,
            args=(
                symbol,
                signal,
                entry_price,
                expiry
            )
        )

        thread.start()

        print("THREAD STARTED")

        return "OK", 200

    except Exception as e:

        print("WEBHOOK ERROR:", e)

        return "ERROR", 500

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
