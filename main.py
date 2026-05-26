import os
import time
import threading
import requests
import random
from datetime import datetime, timedelta
import pytz
import pandas as pd
import yfinance as yf

from flask import Flask
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator

# =========================
# BOT CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

india = pytz.timezone("Asia/Kolkata")

pairs = [
    "EURUSD=X",
    "GBPUSD=X",
    "USDJPY=X",
    "AUDUSD=X",
    "USDCAD=X",
    "USDCHF=X",
    "EURJPY=X"
]

# =========================
# STATS
# =========================

wins = 0
losses = 0
total = 0

# =========================
# TELEGRAM
# =========================

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except Exception as e:
        print("TELEGRAM ERROR:", e)

# =========================
# MARKET DATA
# =========================

def get_data(symbol):
    try:
        df = yf.download(symbol, interval="1m", period="1d", progress=False)
        return df
    except:
        return None

# =========================
# SIGNAL ENGINE (REAL LOGIC)
# =========================

def generate_signal(symbol):

    df = get_data(symbol)
    if df is None or len(df) < 50:
        return None

    close = df["Close"]

    ema9 = EMAIndicator(close, window=9).ema_indicator()
    ema21 = EMAIndicator(close, window=21).ema_indicator()
    rsi = RSIIndicator(close, window=14).rsi()
    macd = MACD(close)

    macd_line = macd.macd()
    signal_line = macd.macd_signal()

    price = float(close.iloc[-1])

    buy_score = 0
    sell_score = 0

    if ema9.iloc[-1] > ema21.iloc[-1]:
        buy_score += 1
    else:
        sell_score += 1

    if rsi.iloc[-1] > 50:
        buy_score += 1
    else:
        sell_score += 1

    if macd_line.iloc[-1] > signal_line.iloc[-1]:
        buy_score += 1
    else:
        sell_score += 1

    if buy_score >= 2:
        return symbol, "BUY", "UP ⬆️", price

    if sell_score >= 2:
        return symbol, "SELL", "DOWN ⬇️", price

    return None

# =========================
# RESULT CHECK
# =========================

def check_result(symbol, direction, entry_price, minutes):

    global wins, losses, total

    time.sleep(minutes * 60)

    df = get_data(symbol)

    if df is None:
        return

    exit_price = float(df["Close"].iloc[-1])

    if direction == "BUY":
        result = "WIN ✅" if exit_price > entry_price else "LOSS ❌"
    else:
        result = "WIN ✅" if exit_price < entry_price else "LOSS ❌"

    total += 1

    if "WIN" in result:
        wins += 1
    else:
        losses += 1

    winrate = round((wins / total) * 100, 2)

    msg = f"""
━━━━━━━━━━━━━━
📊 RESULT UPDATE

📈 Asset: {symbol.replace('=X','')}

💰 Entry: {entry_price}
💵 Exit: {exit_price}

🏁 Result: {result}

━━━━━━━━━━━━━━
📊 SUMMARY

Total: {total}
Wins: {wins}
Losses: {losses}
Win Rate: {winrate}%
━━━━━━━━━━━━━━
"""

    send(msg)

# =========================
# SIGNAL LOOP (24/7)
# =========================

def engine():

    global total

    while True:

        try:

            random.shuffle(pairs)

            for symbol in pairs:

                signal = generate_signal(symbol)

                if signal:

                    symbol, direction, arrow, price = signal

                    now = datetime.now(india)

                    minutes = random.choice([1, 2, 5])

                    entry_time = now + timedelta(minutes=1)
                    expiry_time = entry_time + timedelta(minutes=minutes)

                    total += 1

                    msg = f"""
━━━━━━━━━━━━━━
📢 AI BINARY SIGNAL

📈 Asset : {symbol.replace('=X','')}

🕒 Signal Time :
{now.strftime("%I:%M:%S %p")}

⏰ Entry Time :
{entry_time.strftime("%I:%M %p")}

⌛ Expiry Time :
{expiry_time.strftime("%I:%M %p")}

⏳ Trade :
{minutes} MIN

📊 Direction :
{arrow}

💰 Entry Price :
{price}

🔥 Strategy :
EMA + RSI + MACD Trend Engine
━━━━━━━━━━━━━━
"""

                    send(msg)

                    threading.Thread(
                        target=check_result,
                        args=(symbol, direction, price, minutes)
                    ).start()

                    time.sleep(120)

                    break

            time.sleep(30)

        except Exception as e:
            print("ENGINE ERROR:", e)
            time.sleep(10)

# =========================
# FLASK SERVER
# =========================

@app.route("/")

def home():
    return "BOT RUNNING 24/7"

# =========================
# START
# =========================

threading.Thread(target=engine).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
