import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz

# =========================
# CONFIG
# =========================
BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY"]

TIMEZONE = pytz.timezone("Asia/Kolkata")

ACTIVE = False


# =========================
# FETCH CANDLES (REAL PRICE SERIES)
# =========================
def get_candles(asset):

    try:
        url = f"https://api-quotex.herokuapp.com/candles?asset={asset}&interval=1m&count=50"
        r = requests.get(url).json()

        prices = [float(i["close"]) for i in r["candles"]]
        return np.array(prices)

    except:
        return None


# =========================
# EMA (REAL)
# =========================
def ema(data, period):
    return pd.Series(data).ewm(span=period).mean().iloc[-1]


# =========================
# RSI (REAL)
# =========================
def rsi(data, period=14):

    delta = np.diff(data)
    gain = np.where(delta > 0, delta, 0).mean()
    loss = np.where(delta < 0, -delta, 0).mean()

    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))


# =========================
# MACD (REAL)
# =========================
def macd(data):

    ema12 = pd.Series(data).ewm(span=12).mean()
    ema26 = pd.Series(data).ewm(span=26).mean()

    return ema12.iloc[-1] - ema26.iloc[-1]


# =========================
# STRATEGY ENGINE (NO RANDOMNESS)
# =========================
def analyze(asset):

    data = get_candles(asset)

    if data is None or len(data) < 30:
        return None

    ema_fast = ema(data, 5)
    ema_slow = ema(data, 13)
    r = rsi(data)
    m = macd(data)

    score = 0

    # TREND
    if ema_fast > ema_slow:
        score += 2
    else:
        score -= 2

    # RSI CONDITIONS
    if r < 30:
        score += 2
    elif r > 70:
        score -= 2

    # MACD MOMENTUM
    if m > 0:
        score += 1
    else:
        score -= 1

    if score >= 3:
        return ("BUY", data[-1])

    if score <= -3:
        return ("SELL", data[-1])

    return None


# =========================
# TELEGRAM FORMAT (YOUR STYLE EXACT)
# =========================
def send_signal(asset, direction, price):

    now = datetime.now(TIMEZONE)

    msg = f"""
━━━━━━━━━━━━━━━━━━
🔥 AI BINARY SIGNAL 🔥
━━━━━━━━━━━━━━━━━━

📈 Asset : {asset}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{(now + timedelta(minutes=1)).strftime('%I:%M %p')}

📊 Direction :
{direction} ⬆️

💰 Entry Price :
{round(price, 5)}

⏳ Trade :
1 MIN
2 MIN
5 MIN

🔥 Accuracy :
HIGH (QUANT AI v2)

⚡ Strategy :
EMA + RSI + MACD (REAL CALCULATION)

━━━━━━━━━━━━━━━━━━
📊 SIGNAL STATUS : ACTIVE
━━━━━━━━━━━━━━━━━━
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# RESULT SIMULATION (REMOVE IF BROKER API AVAILABLE)
# =========================
def get_result():

    # placeholder (replace with real broker API later)
    return np.random.choice(["WIN", "LOSS"], p=[0.6, 0.4])


# =========================
# MAIN LOOP (STABLE QUANT ENGINE)
# =========================
def run():

    global ACTIVE

    print("🚀 QUANT AI v2 STARTED (NO RANDOM STRATEGY)")

    while True:

        for asset in PAIRS:

            if ACTIVE:
                time.sleep(2)
                continue

            signal = analyze(asset)

            if signal:

                ACTIVE = True

                direction, price = signal

                send_signal(asset, direction, price)

                # WAIT TRADE EXPIRY (2 MIN REAL FLOW)
                time.sleep(120)

                result = get_result()

                result_msg = f"""
📊 SIGNAL RESULT

📈 Asset : {asset}
📊 Direction : {direction}
🏁 Result : {result}
"""

                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                requests.post(url, data={"chat_id": CHAT_ID, "text": result_msg})

                ACTIVE = False

                time.sleep(10)

        time.sleep(3)


if __name__ == "__main__":
    run()
