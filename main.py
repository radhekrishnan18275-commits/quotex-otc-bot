import os
import asyncio
import requests
import yfinance as yf

from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Bot

# =========================================
# SETTINGS
# =========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# =========================================
# SEND TELEGRAM MESSAGE
# =========================================

async def send_telegram_message(message):

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

# =========================================
# GET LIVE FOREX PRICE
# =========================================

def get_live_price(symbol):

    try:

        pair = symbol.replace("/", "")

        forex_map = {
            "EURUSD": "EURUSD=X",
            "GBPUSD": "GBPUSD=X",
            "AUDUSD": "AUDUSD=X",
            "USDJPY": "JPY=X",
            "USDCHF": "CHF=X",
            "USDCAD": "CAD=X"
        }

        ticker = forex_map.get(pair, "EURUSD=X")

        data = yf.Ticker(ticker)

        candles = data.history(
            period="1d",
            interval="1m"
        )

        if not candles.empty:

            price = candles["Close"].iloc[-1]

            return float(price)

    except Exception as e:

        print("PRICE FETCH ERROR:", e)

    return None

# =========================================
# CHECK RESULT
# =========================================

def check_trade_result(symbol, signal, entry_price):

    final_price = get_live_price(symbol)

    if final_price is None:

        return "UNKNOWN"

    if signal == "BUY":

        if final_price > entry_price:
            return "WIN"
        else:
            return "LOSS"

    if signal == "SELL":

        if final_price < entry_price:
            return "WIN"
        else:
            return "LOSS"

    return "UNKNOWN"

# =========================================
# RESULT ENGINE
# =========================================

async def result_engine(
    symbol,
    signal,
    entry_price,
    expiry_minutes
):

    await asyncio.sleep(expiry_minutes * 60)

    result = check_trade_result(
        symbol,
        signal,
        entry_price
    )

    if result == "WIN":

        result_message = f"""
━━━━━━━━━━━━━━
✅ RESULT : WIN

📈 Asset : {symbol}

🔥 Direction : {signal}

💰 Profit Trade
━━━━━━━━━━━━━━
"""

    else:

        result_message = f"""
━━━━━━━━━━━━━━
❌ RESULT : LOSS

📉 Asset : {symbol}

⚠ Market Reversed
━━━━━━━━━━━━━━
"""

    await send_telegram_message(result_message)

# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return "AI Binary Bot Running 🚀"

# =========================================
# WEBHOOK
# =========================================

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

        now = datetime.now()

        entry_time = now + timedelta(minutes=1)

        expiry_time = (
            entry_time +
            timedelta(minutes=expiry)
        )

        entry_price = get_live_price(symbol)

        if entry_price is None:

            return "PRICE ERROR", 500

        message = f"""
━━━━━━━━━━━━━━
📊 AI OTC SIGNAL

Asset : {symbol}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{entry_time.strftime('%I:%M %p')}

⌛ Expiry Time :
{expiry_time.strftime('%I:%M %p')}

📈 Direction :
{direction}

🔥 Accuracy : HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation
━━━━━━━━━━━━━━
"""

        asyncio.run(
            send_telegram_message(message)
        )

        asyncio.run(
            result_engine(
                symbol,
                signal,
                entry_price,
                expiry
            )
        )

        return "OK", 200

    except Exception as e:

        print("WEBHOOK ERROR:", e)

        return "ERROR", 500

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
