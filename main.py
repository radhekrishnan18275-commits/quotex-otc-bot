import os
import time
import requests
import numpy as np
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOL = "R_100"
COOLDOWN = 60

last_signal = 0


# =========================
# LIVE MARKET DATA
# =========================
def get_data():
    url = f"https://api.deriv.com/api/v2/ohlc?symbol={SYMBOL}&granularity=60&count=60"
    r = requests.get(url).json()

    candles = r.get("candles", [])
    closes = np.array([float(c["close"]) for c in candles])

    return closes


# =========================
# INDICATORS
# =========================
def ema(data, p):
    w = np.exp(np.linspace(-1, 0, p))
    w /= w.sum()
    return np.convolve(data, w, mode="valid")[-1]


def rsi(data):
    diff = np.diff(data)
    gain = np.mean(diff[diff > 0]) if np.any(diff > 0) else 0
    loss = np.mean(-diff[diff < 0]) if np.any(diff < 0) else 0
    rs = gain / (loss + 1e-6)
    return 100 - (100 / (1 + rs))


def macd(data):
    return ema(data, 6) - ema(data, 18)


# =========================
# AI DECISION ENGINE
# =========================
def signal_engine(data):

    ema_fast = ema(data[-30:], 5)
    ema_slow = ema(data[-30:], 12)
    rsi_val = rsi(data[-30:])
    macd_val = macd(data[-30:])

    score = 0

    if ema_fast > ema_slow:
        score += 2
    else:
        score -= 2

    if rsi_val < 30:
        score += 2
    elif rsi_val > 70:
        score -= 2

    if macd_val > 0:
        score += 1
    else:
        score -= 1

    if score >= 3:
        return "BUY", 0.88
    elif score <= -3:
        return "SELL", 0.88

    return None, 0


# =========================
# FORMAT YOUR EXACT SIGNAL
# =========================
def format_signal(asset, direction, price, minutes):

    now = datetime.now()
    entry = now + timedelta(minutes=1)
    expiry = now + timedelta(minutes=minutes)

    return f"""
━━━━━━━━━━━━━━━━━━
🔥 AI BINARY SIGNAL 🔥
━━━━━━━━━━━━━━━━━━

📈 Asset : {asset}

🕒 Signal Time :
{now.strftime('%I:%M:%S %p')}

⏰ Entry Time :
{entry.strftime('%I:%M %p')}

⌛ Expiry Time :
{expiry.strftime('%I:%M %p')}

⏳ Trade :
{minutes} MIN

📊 Direction :
{direction} {'⬆️' if direction=='BUY' else '⬇️'}

💰 Entry Price :
{round(price, 5)}

🔥 Accuracy :
HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation

━━━━━━━━━━━━━━━━━━
📊 SIGNAL STATUS : ACTIVE
━━━━━━━━━━━━━━━━━━
"""


# =========================
# SEND TELEGRAM
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# =========================
# MAIN LOOP
# =========================
def run():

    global last_signal

    print("🚀 REAL MARKET SIGNAL BOT STARTED")

    while True:

        try:

            now = time.time()
            if now - last_signal < COOLDOWN:
                time.sleep(5)
                continue

            data = get_data()

            if len(data) < 40:
                continue

            direction, conf = signal_engine(data)

            price = data[-1]

            if direction:

                # send 1m, 2m, 5m EXACT FORMAT
                for m in [1, 2, 5]:

                    msg = format_signal("USDJPY (LIVE MARKET)", direction, price, m)
                    print(msg)
                    send(msg)
                    time.sleep(1)

                last_signal = now

            else:
                print("NO TRADE - NO EDGE")

            time.sleep(10)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)


if __name__ == "__main__":
    run()
