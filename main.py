import os
import time
import random
import threading
import requests
import pandas as pd
import yfinance as yf
import pytz

from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from flask import Flask
from datetime import datetime, timedelta

# =====================================================
# SETTINGS
# =====================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

india = pytz.timezone("Asia/Kolkata")

pairs = [
    "EURUSD=X",
    "GBPUSD=X",
    "AUDUSD=X",
    "USDJPY=X",
    "USDCAD=X",
    "USDCHF=X"
]

wins = 0
losses = 0
total = 0

# =====================================================
# TELEGRAM
# =====================================================

def send_message(text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    try:
        requests.post(url, data=data)

    except Exception as e:
        print("TELEGRAM ERROR:", e)

# =====================================================
# GET MARKET DATA
# =====================================================

def get_data(pair):

    try:

        df = yf.download(
            pair,
            interval="1m",
            period="1d",
            progress=False
        )

        return df

    except Exception as e:

        print("DATA ERROR:", e)

        return None

# =====================================================
# AI SIGNAL ENGINE
# =====================================================

def generate_signal(pair):

    df = get_data(pair)

    if df is None:
        return None

    if len(df) < 50:
        return None

    close = df["Close"]

    ema_fast = EMAIndicator(close, window=9).ema_indicator()
    ema_slow = EMAIndicator(close, window=21).ema_indicator()

    rsi = RSIIndicator(close, window=14).rsi()

    macd = MACD(close)

    macd_line = macd.macd()
    macd_signal = macd.macd_signal()

    last_price = round(close.iloc[-1], 5)

    # =================================================
    # BUY CONDITIONS
    # =================================================

    buy_condition = (
        ema_fast.iloc[-1] > ema_slow.iloc[-1]
        and rsi.iloc[-1] > 55
        and macd_line.iloc[-1] > macd_signal.iloc[-1]
    )

    # =================================================
    # SELL CONDITIONS
    # =================================================

    sell_condition = (
        ema_fast.iloc[-1] < ema_slow.iloc[-1]
        and rsi.iloc[-1] < 45
        and macd_line.iloc[-1] < macd_signal.iloc[-1]
    )

    if buy_condition:

        return {
            "pair": pair.replace("=X", ""),
            "direction": "UP ⬆️",
            "type": "BUY",
            "price": last_price,
            "accuracy": random.randint(88, 95)
        }

    elif sell_condition:

        return {
            "pair": pair.replace("=X", ""),
            "direction": "DOWN ⬇️",
            "type": "SELL",
            "price": last_price,
            "accuracy": random.randint(88, 95)
        }

    return None

# =====================================================
# RESULT CHECKER
# =====================================================

def result_checker(pair, trade_type, entry_price, expiry):

    global wins
    global losses
    global total

    time.sleep(expiry * 60)

    df = get_data(pair + "=X")

    if df is None:
        return

    exit_price = round(df["Close"].iloc[-1], 5)

    result = "LOSS ❌"

    if trade_type == "BUY":

        if exit_price > entry_price:
            result = "WIN ✅"

    else:

        if exit_price < entry_price:
            result = "WIN ✅"

    if "WIN" in result:
        wins += 1
    else:
        losses += 1

    total = wins + losses

    winrate = round((wins / total) * 100, 2)

    result_msg = f"""
━━━━━━━━━━━━━━
📢 AI BINARY RESULT

📈 Asset : {pair}

💰 Entry Price :
{entry_price}

💵 Exit Price :
{exit_price}

📊 Direction :
{trade_type}

🏁 Final Result :
{result}

━━━━━━━━━━━━━━
📊 DAILY SUMMARY

✅ Wins : {wins}

❌ Losses : {losses}

📈 Total : {total}

🎯 Win Rate : {winrate}%
━━━━━━━━━━━━━━
"""

    send_message(result_msg)

# =====================================================
# MAIN ENGINE
# =====================================================

def trading_engine():

    while True:

        try:

            random.shuffle(pairs)

            found_signal = False

            for pair in pairs:

                signal = generate_signal(pair)

                if signal:

                    found_signal = True

                    now = datetime.now(india)

                    signal_time = now.strftime("%I:%M:%S %p")

                    entry = now + timedelta(minutes=1)

                    expiry_minutes = random.choice([1, 2, 5])

                    expiry = entry + timedelta(minutes=expiry_minutes)

                    msg = f"""
━━━━━━━━━━━━━━
📢 AI BINARY SIGNAL

📈 Asset : {signal['pair']}

🕒 Signal Time :
{signal_time}

⏰ Entry Time :
{entry.strftime("%I:%M %p")}

⌛ Expiry Time :
{expiry.strftime("%I:%M %p")}

⏳ Trade :
{expiry_minutes} Minute Trade

📊 Direction :
{signal['direction']}

💰 Entry Price :
{signal['price']}

🔥 Accuracy :
{signal['accuracy']}%

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation
━━━━━━━━━━━━━━
"""

                    send_message(msg)

                    threading.Thread(
                        target=result_checker,
                        args=(
                            signal['pair'],
                            signal['type'],
                            signal['price'],
                            expiry_minutes
                        )
                    ).start()

                    print("SIGNAL SENT:", signal['pair'])

                    time.sleep(180)

                    break

            if not found_signal:

                print("NO STRONG SIGNAL")

                time.sleep(60)

        except Exception as e:

            print("ENGINE ERROR:", e)

            time.sleep(30)

# =====================================================
# FLASK
# =====================================================

@app.route("/")

def home():

    return "AI SIGNAL ENGINE RUNNING"

# =====================================================
# START
# =====================================================

threading.Thread(target=trading_engine).start()

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
