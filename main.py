import os
import time
import requests
from datetime import datetime, timedelta

import numpy as np

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

COOLDOWN_SECONDS = 60

last_signal_time = 0

# =========================
# SIMPLE MARKET SIMULATION
# (Replace with real broker API later)
# =========================
def get_market_data(asset="USDJPY"):
    # Fake candles for demo (replace with Quotex/MT5 data feed)
    closes = np.random.normal(1.0900, 0.0010, 50)
    return closes


# =========================
# INDICATORS
# =========================
def ema(data, period=10):
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    return np.convolve(data, weights, mode='valid')[-1]


def rsi(data, period=14):
    diff = np.diff(data)
    gain = np.maximum(diff, 0).mean()
    loss = -np.minimum(diff, 0).mean()
    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))


# =========================
# AI SIGNAL ENGINE
# =========================
def analyze_market(data):

    ema_fast = ema(data[-20:], 5)
    ema_slow = ema(data[-20:], 10)
    rsi_val = rsi(data[-20:])

    macd = ema_fast - ema_slow

    score = 0

    # Trend logic
    if ema_fast > ema_slow:
        score += 1
    else:
        score -= 1

    # RSI logic
    if rsi_val < 30:
        score += 1
    elif rsi_val > 70:
        score -= 1

    # MACD logic
    if macd > 0:
        score += 1
    else:
        score -= 1

    if score >= 2:
        return "BUY", 0.85
    elif score <= -2:
        return "SELL", 0.85
    else:
        return None, 0.40


# =========================
# FORMAT SIGNAL
# =========================
def format_signal(asset, direction, price, expiry):

    now = datetime.now()

    entry_time = now + timedelta(minutes=1)
    expiry_time = now + timedelta(minutes=expiry)

    arrow = "⬆️" if direction == "BUY" else "⬇️"

    return f"""
━━━━━━━━━━━━━━━━━━
🔥 AI SMART SIGNAL BOT 🔥
━━━━━━━━━━━━━━━━━━

📈 Asset : {asset}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{entry_time.strftime('%I:%M %p')}

⌛ Expiry Time :
{expiry_time.strftime('%I:%M %p')}

⏳ Trade :
{expiry} MIN

📊 Direction :
{direction} {arrow}

💰 Entry Price :
{round(price, 5)}

🔥 Confidence :
HIGH

⚡ AI Engine :
EMA + RSI + MACD Fusion

━━━━━━━━━━━━━━━━━━
"""


# =========================
# TELEGRAM
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# BOT LOOP
# =========================
def run():

    global last_signal_time

    print("🚀 AI SMART SIGNAL BOT STARTED")

    while True:

        try:
            now = time.time()

            # cooldown to avoid spam
            if now - last_signal_time < COOLDOWN_SECONDS:
                time.sleep(5)
                continue

            data = get_market_data()

            direction, confidence = analyze_market(data)

            if direction is None:
                print("NO TRADE - LOW CONFIDENCE")
                time.sleep(5)
                continue

            price = data[-1]

            # only HIGH quality signals
            if confidence >= 0.80:

                for expiry in [1, 2, 5]:

                    msg = format_signal("USDJPY", direction, price, expiry)
                    print(msg)
                    send(msg)

                    time.sleep(1)

                last_signal_time = now

            time.sleep(10)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)


if __name__ == "__main__":
    run()
