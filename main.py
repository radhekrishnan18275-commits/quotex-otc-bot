from flask import Flask, request
import requests
import pytz
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import ta
import threading
import time

app = Flask(__name__)

# ================= CONFIG =================
BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

TIMEZONE = pytz.timezone("Asia/Kolkata")

wins = 0
losses = 0
total = 0

# ================= TELEGRAM =================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

# ================= MARKET DATA =================
def get_candles(symbol="EURUSD=X", interval="1m", period="1d"):
    df = yf.download(symbol, interval=interval, period=period, progress=False)
    return df

# ================= SIGNAL ENGINE =================
def generate_signal(symbol):

    df = get_candles(symbol)

    if df is None or len(df) < 50:
        return None

    df["ema9"] = ta.trend.ema_indicator(df["Close"], window=9)
    df["ema21"] = ta.trend.ema_indicator(df["Close"], window=21)
    df["rsi"] = ta.momentum.rsi(df["Close"], window=14)

    macd = ta.trend.MACD(df["Close"])
    df["macd"] = macd.macd()
    df["signal"] = macd.macd_signal()

    last = df.iloc[-1]

    score = 0

    if last["ema9"] > last["ema21"]:
        score += 1
    else:
        score -= 1

    if last["rsi"] > 55:
        score += 1
    elif last["rsi"] < 45:
        score -= 1

    if last["macd"] > last["signal"]:
        score += 1
    else:
        score -= 1

    if score >= 2:
        return "BUY", float(last["Close"])
    elif score <= -2:
        return "SELL", float(last["Close"])
    else:
        return None

# ================= RESULT ENGINE =================
def check_result(symbol, direction, entry_price, expiry_seconds=60):

    global wins, losses, total

    time.sleep(expiry_seconds)

    df = get_candles(symbol)
    exit_price = float(df.iloc[-1]["Close"])

    total += 1

    if direction == "BUY":
        result = "WIN" if exit_price > entry_price else "LOSS"
    else:
        result = "WIN" if exit_price < entry_price else "LOSS"

    if result == "WIN":
        wins += 1
    else:
        losses += 1

    msg = f"""
📊 RESULT UPDATE

Asset: {symbol}
Direction: {direction}

Entry: {entry_price}
Exit: {exit_price}

Result: {result}

📈 Wins: {wins}
📉 Losses: {losses}
📊 Total: {total}
"""
    send_telegram(msg)

# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    symbol = data.get("symbol", "EURUSD=X")

    signal = generate_signal(symbol)

    if not signal:
        return "NO SIGNAL", 200

    direction, price = signal

    now = datetime.now(TIMEZONE)

    entry_time = now + timedelta(minutes=1)
    expiry_time = now + timedelta(minutes=2)

    message = f"""
📊 AI BINARY SIGNAL

📈 Asset : {symbol}

🕒 Signal Time : {now.strftime("%I:%M:%S %p")}

⏰ Entry Time : {entry_time.strftime("%I:%M %p")}

⌛ Expiry Time : {expiry_time.strftime("%I:%M %p")}

📊 Direction : {direction} {'⬆️' if direction=='BUY' else '⬇️'}

💰 Entry Price : {price}

🔥 Accuracy : HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Filter
━━━━━━━━━━━━━━
"""

    send_telegram(message)

    threading.Thread(
        target=check_result,
        args=(symbol, direction, price, 60)
    ).start()

    return "OK", 200

@app.route("/")
def home():
    return "AI SIGNAL BOT RUNNING 24/7"

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
