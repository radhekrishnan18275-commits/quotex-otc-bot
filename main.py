import os
import time
import requests
import numpy as np
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

DERIV_APP_ID = "1089"  # public demo app id
SYMBOL = "R_100"       # Volatility index (fast OTC-like movement)

COOLDOWN = 60
last_signal = 0


# =========================
# GET LIVE CANDLES (DERIV)
# =========================
def get_candles(count=50):

    url = f"https://api.deriv.com/api/v2/ohlc?symbol={SYMBOL}&granularity=60&count={count}"

    r = requests.get(url)
    data = r.json()

    candles = data.get("candles", [])

    closes = [float(c["close"]) for c in candles if "close" in c]

    return np.array(closes)


# =========================
# INDICATORS
# =========================
def ema(data, period):
    weights = np.exp(np.linspace(-1, 0, period))
    weights /= weights.sum()
    return np.convolve(data, weights, mode="valid")[-1]


def rsi(data, period=14):
    diff = np.diff(data)
    gain = np.mean(np.where(diff > 0, diff, 0))
    loss = np.mean(np.where(diff < 0, -diff, 0))

    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))


# =========================
# AI ENGINE (PRO)
# =========================
def analyze(data):

    ema_fast = ema(data[-30:], 5)
    ema_slow = ema(data[-30:], 12)
    rsi_val = rsi(data[-30:])
    macd = ema_fast - ema_slow

    score = 0

    # Trend
    if ema_fast > ema_slow:
        score += 2
    else:
        score -= 2

    # RSI
    if rsi_val < 30:
        score += 2
    elif rsi_val > 70:
        score -= 2

    # MACD
    if macd > 0:
        score += 1
    else:
        score -= 1

    if score >= 3:
        return "BUY", 0.90
    elif score <= -3:
        return "SELL", 0.90

    return None, 0.0


# =========================
# FORMAT SIGNAL
# =========================
def format_signal(asset, direction, price, expiry, confidence):

    now = datetime.now()

    arrow = "⬆️" if direction == "BUY" else "⬇️"

    return f"""
━━━━━━━━━━━━━━━━━━
🔥 PRO AI SIGNAL BOT 🔥
━━━━━━━━━━━━━━━━━━

📈 Asset : {asset}

🕒 Time :
{now.strftime('%I:%M:%S %p')}

⏳ Trade :
{expiry} MIN

📊 Direction :
{direction} {arrow}

💰 Price :
{round(price, 5)}

🎯 Confidence :
{int(confidence*100)}%

⚡ Engine :
EMA + RSI + MACD (Live Market)

━━━━━━━━━━━━━━━━━━
"""


# =========================
# TELEGRAM
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# MAIN LOOP
# =========================
def run():

    global last_signal

    print("🚀 PRO AI BOT STARTED (LIVE MARKET)")

    while True:

        try:
            now = time.time()

            if now - last_signal < COOLDOWN:
                time.sleep(5)
                continue

            data = get_candles()

            if len(data) < 30:
                time.sleep(5)
                continue

            direction, confidence = analyze(data)

            price = data[-1]

            if direction and confidence >= 0.85:

                for expiry in [1, 2, 5]:

                    msg = format_signal("LIVE MARKET", direction, price, expiry, confidence)
                    print(msg)
                    send(msg)

                    time.sleep(1)

                last_signal = now

            else:
                print("NO TRADE - LOW QUALITY SETUP")

            time.sleep(10)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)


if __name__ == "__main__":
    run()
