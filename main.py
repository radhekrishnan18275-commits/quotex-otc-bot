import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime
import pytz

# =========================
# CONFIG
# =========================
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN"
CHAT_ID = "PUT_YOUR_CHAT_ID"

PAIRS = ["EURUSD", "GBPUSD", "USDJPY"]

tz = pytz.timezone("Asia/Kolkata")

active = False


# =========================
# GET REAL CANDLES
# =========================
def get_data(symbol):
    try:
        url = f"https://api-quotex.herokuapp.com/candles?asset={symbol}&interval=1m&count=50"
        r = requests.get(url, timeout=10).json()

        closes = [float(i["close"]) for i in r["candles"]]
        return np.array(closes)

    except:
        return None


# =========================
# INDICATORS (REAL)
# =========================
def ema(data, period):
    return pd.Series(data).ewm(span=period).mean().iloc[-1]


def rsi(data):
    diff = np.diff(data)
    gain = np.mean([x for x in diff if x > 0]) if np.any(diff > 0) else 0
    loss = np.mean([-x for x in diff if x < 0]) if np.any(diff < 0) else 0

    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))


def macd(data):
    ema12 = pd.Series(data).ewm(span=12).mean()
    ema26 = pd.Series(data).ewm(span=26).mean()
    return ema12.iloc[-1] - ema26.iloc[-1]


# =========================
# STRATEGY (NO RANDOM)
# =========================
def analyze(symbol):

    data = get_data(symbol)
    if data is None or len(data) < 30:
        return None

    e1 = ema(data, 5)
    e2 = ema(data, 13)
    r = rsi(data)
    m = macd(data)

    score = 0

    if e1 > e2:
        score += 2
    else:
        score -= 2

    if r < 30:
        score += 2
    elif r > 70:
        score -= 2

    if m > 0:
        score += 1
    else:
        score -= 1

    if score >= 3:
        return "BUY", data[-1]
    elif score <= -3:
        return "SELL", data[-1]

    return None


# =========================
# TELEGRAM FORMAT (YOUR STYLE)
# =========================
def send_signal(symbol, direction, price):

    now = datetime.now(tz)

    msg = f"""
━━━━━━━━━━━━━━━━━━
🔥 AI BINARY SIGNAL 🔥
━━━━━━━━━━━━━━━━━━

📈 Asset : {symbol}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{now.strftime('%I:%M %p')}

📊 Direction :
{direction} ⬆️

💰 Entry Price :
{round(price, 5)}

⏳ Trade :
1 MIN
2 MIN
5 MIN

🔥 Accuracy :
HIGH

⚡ Strategy :
EMA + RSI + MACD (REAL)

━━━━━━━━━━━━━━━━━━
📊 SIGNAL STATUS : ACTIVE
━━━━━━━━━━━━━━━━━━
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# MAIN LOOP (NO SPAM)
# =========================
def run():

    global active

    print("🚀 CLEAN QUANT BOT STARTED")

    while True:

        for symbol in PAIRS:

            if active:
                time.sleep(2)
                continue

            signal = analyze(symbol)

            if signal:

                active = True

                direction, price = signal

                send_signal(symbol, direction, price)

                # wait trade time
                time.sleep(120)

                active = False

                time.sleep(5)

        time.sleep(3)


if __name__ == "__main__":
    run()
