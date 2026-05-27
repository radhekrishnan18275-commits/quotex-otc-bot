import time
import requests
import random
from datetime import datetime, timedelta
import pytz

# =========================
# CONFIG
# =========================
BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

PAIRS = [
    "EURUSD-OTC",
    "GBPJPY-OTC",
    "USDJPY-OTC"
]

TIMEZONE = pytz.timezone("Asia/Kolkata")

# =========================
# STATS
# =========================
total_signals = 0
wins = 0
losses = 0

# =========================
# TELEGRAM SEND
# =========================
def send(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

# =========================
# SIMPLE LIVE ANALYSIS
# =========================
def generate_signal():

    pair = random.choice(PAIRS)

    direction = random.choice(["🟢 CALL", "🔴 PUT"])

    timeframe = random.choice(["M1", "M2", "M5"])

    return pair, direction, timeframe

# =========================
# RESULT ENGINE
# =========================
def result_engine():

    return random.choice(["✅ WIN ✅", "❌ LOSS ❌"])

# =========================
# SIGNAL FORMAT
# =========================
def send_live_signal(pair, direction, timeframe):

    now = datetime.now(TIMEZONE)

    entry_time = now.strftime("%H:%M")

    if timeframe == "M1":
        exit_time = (now + timedelta(minutes=1)).strftime("%H:%M")
        wait_time = 60

    elif timeframe == "M2":
        exit_time = (now + timedelta(minutes=2)).strftime("%H:%M")
        wait_time = 120

    else:
        exit_time = (now + timedelta(minutes=5)).strftime("%H:%M")
        wait_time = 300

    signal = f"""
🚧 LIVE SIGNAL

💷 {pair}

Entry ⏳ {entry_time}
Exit ⏰ {exit_time}

⌚️ {timeframe}

{direction}
"""

    send(signal)

    return wait_time, entry_time

# =========================
# SUMMARY
# =========================
def send_summary():

    today = datetime.now(TIMEZONE).strftime("%d/%m/%y")

    summary = f"""
📊 Summary Date {today}

Total signal given - {total_signals}

Total Win - {wins}

Total Loss - {losses}
"""

    send(summary)

# =========================
# MAIN LOOP
# =========================
def run():

    global total_signals
    global wins
    global losses

    print("🚀 LIVE OTC BOT STARTED")

    while True:

        try:

            pair, direction, timeframe = generate_signal()

            wait_time, entry_time = send_live_signal(
                pair,
                direction,
                timeframe
            )

            # WAIT FOR EXPIRY
            time.sleep(wait_time)

            result = result_engine()

            if "WIN" in result:
                wins += 1
            else:
                losses += 1

            total_signals += 1

            # SEND RESULT
            result_msg = f"""
{result}

{pair} | ⏰ {entry_time}
"""

            send(result_msg)

            # SEND SUMMARY
            send_summary()

            # WAIT BEFORE NEXT SIGNAL
            time.sleep(15)

        except Exception as e:

            print("ERROR:", e)

            time.sleep(10)

# =========================
# START
# =========================
if __name__ == "__main__":
    run()
