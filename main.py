from flask import Flask, request, jsonify
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

stats = {
    "wins": 0,
    "losses": 0,
    "total": 0,
    "signals": []
}

# ================= TELEGRAM =================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ================= MARKET DATA =================
def get_data(symbol="EURUSD=X", interval="1m"):
    return yf.download(symbol, interval=interval, period="1d", progress=False)

# ================= MULTI TIMEFRAME ENGINE =================
def analyze(symbol):

    df1 = yf.download(symbol, interval="1m", period="1d", progress=False)
    df5 = yf.download(symbol, interval="5m", period="5d", progress=False)

    if len(df1) < 50 or len(df5) < 50:
        return None

    def score(df):
        df["ema9"] = ta.trend.ema_indicator(df["Close"], 9)
        df["ema21"] = ta.trend.ema_indicator(df["Close"], 21)
        df["rsi"] = ta.momentum.rsi(df["Close"], 14)

        macd = ta.trend.MACD(df["Close"])
        df["macd"] = macd.macd()
        df["signal"] = macd.macd_signal()

        last = df.iloc[-1]

        s = 0
        if last["ema9"] > last["ema21"]:
            s += 1
        else:
            s -= 1

        if last["rsi"] > 55:
            s += 1
        elif last["rsi"] < 45:
            s -= 1

        if last["macd"] > last["signal"]:
            s += 1
        else:
            s -= 1

        return s

    s1 = score(df1)
    s5 = score(df5)

    final_score = s1 + s5

    price = float(df1.iloc[-1]["Close"])

    if final_score >= 3:
        return "BUY", price, final_score
    elif final_score <= -3:
        return "SELL", price, final_score
    else:
        return None

# ================= RESULT ENGINE =================
def check_result(symbol, direction, entry_price, expiry=60):

    time.sleep(expiry)

    df = yf.download(symbol, interval="1m", period="1d", progress=False)
    exit_price = float(df.iloc[-1]["Close"])

    stats["total"] += 1

    if direction == "BUY":
        result = "WIN" if exit_price > entry_price else "LOSS"
    else:
        result = "WIN" if exit_price < entry_price else "LOSS"

    if result == "WIN":
        stats["wins"] += 1
    else:
        stats["losses"] += 1

    send_telegram(f"""
📊 RESULT UPDATE

Asset: {symbol}
Direction: {direction}

Entry: {entry_price}
Exit: {exit_price}

Result: {result}

📈 Wins: {stats["wins"]}
📉 Losses: {stats["losses"]}
📊 Total: {stats["total"]}
""")

# ================= WEBHOOK =================
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    symbol = data.get("symbol", "EURUSD=X")

    signal = analyze(symbol)

    if not signal:
        return "NO SIGNAL", 200

    direction, price, score = signal

    now = datetime.now(TIMEZONE)

    entry = now + timedelta(minutes=1)
    expiry = now + timedelta(minutes=2)

    msg = f"""
📊 AI OTC SIGNAL (PRO v3)

📈 Asset : {symbol}

🕒 Signal Time : {now.strftime("%I:%M:%S %p")}

⏰ Entry Time : {entry.strftime("%I:%M %p")}

⌛ Expiry Time : {expiry.strftime("%I:%M %p")}

📊 Direction : {direction}

💰 Entry Price : {price}

🔥 Signal Score : {score}/6

⚡ Strategy :
EMA + RSI + MACD + Multi-Timeframe Trend

━━━━━━━━━━━━━━
"""

    send_telegram(msg)

    stats["signals"].append({
        "symbol": symbol,
        "direction": direction,
        "time": str(now),
        "score": score
    })

    threading.Thread(
        target=check_result,
        args=(symbol, direction, price, 60)
    ).start()

    return "OK", 200

# ================= DASHBOARD =================
@app.route("/")
def dashboard():

    win_rate = 0
    if stats["total"] > 0:
        win_rate = (stats["wins"] / stats["total"]) * 100

    return f"""
    <h1>📊 HEDGE FUND PRO v3 DASHBOARD</h1>
    <p>Wins: {stats['wins']}</p>
    <p>Losses: {stats['losses']}</p>
    <p>Total Trades: {stats['total']}</p>
    <p>Win Rate: {win_rate:.2f}%</p>
    """

# ================= START =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
