import time
import requests
import random
from datetime import datetime, timedelta
import pytz

# =====================================
# CONFIG
# =====================================
BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

PAIRS = [
    "EURUSD-OTC",
    "GBPJPY-OTC",
    "USDJPY-OTC"
]

TIMEZONE = pytz.timezone("Asia/Kolkata")

# =====================================
# STATS
# =====================================
total_signals = 0
wins = 0
losses = 0

# =====================================
# TELEGRAM
# =====================================
def send_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=10
    )

# =====================================
# GET LIVE PRICE
# =====================================
def get_price(pair):

    try:

        url = f"https://api-quotex.herokuapp.com/price?asset={pair}"

        r = requests.get(url, timeout=10).json()

        return float(r["price"])

    except Exception as e:

        print("PRICE ERROR:", e)

        return None

# =====================================
# EMA
# =====================================
def ema(values, period):

    if len(values) < period:
        return sum(values) / len(values)

    multiplier = 2 / (period + 1)

    ema_value = values[0]

    for price in values[1:]:
        ema_value = (price - ema_value) * multiplier + ema_value

    return ema_value

# =====================================
# SIMPLE RSI
# =====================================
def rsi(values, period=14):

    if len(values) < period + 1:
        return 50

    gains = []
    losses = []

    for i in range(1, len(values)):

        diff = values[i] - values[i - 1]

        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains) / period if gains else 0.01
    avg_loss = sum(losses) / period if losses else 0.01

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

# =====================================
# GET REAL CANDLE DATA
# =====================================
def get_candles(pair):

    try:

        url = f"https://api-quotex.herokuapp.com/candles?asset={pair}&interval=1m&count=30"

        r = requests.get(url, timeout=10).json()

        candles = r["candles"]

        closes = [float(c["close"]) for c in candles]

        return closes

    except Exception as e:

        print("CANDLE ERROR:", e)

        return None

# =====================================
# REAL STRATEGY
# =====================================
def analyze_market(pair):

    candles = get_candles(pair)

    if not candles:
        return None

    fast_ema = ema(candles[-10:], 5)
    slow_ema = ema(candles[-20:], 10)

    current_rsi = rsi(candles)

    score = 0

    # TREND
    if fast_ema > slow_ema:
        score += 2
    else:
        score -= 2

    # RSI
    if current_rsi < 35:
        score += 1

    elif current_rsi > 65:
        score -= 1

    # DECISION
    if score >= 2:
        return "CALL"

    elif score <= -2:
        return "PUT"

    return None

# =====================================
# GENERATE SIGNAL
# =====================================
def generate_signal():

    random.shuffle(PAIRS)

    for pair in PAIRS:

        direction = analyze_market(pair)

        if direction:

            timeframe = random.choice(["M1", "M2", "M5"])

            return pair, direction, timeframe

    return None

# =====================================
# SEND SIGNAL
# =====================================
def send_signal(pair, direction, timeframe, entry_price):

    now = datetime.now(TIMEZONE)

    entry_time = now.strftime("%H:%M")

    if timeframe == "M1":
        expiry = now + timedelta(minutes=1)
        wait_seconds = 60

    elif timeframe == "M2":
        expiry = now + timedelta(minutes=2)
        wait_seconds = 120

    else:
        expiry = now + timedelta(minutes=5)
        wait_seconds = 300

    exit_time = expiry.strftime("%H:%M")

    arrow = "🟢" if direction == "CALL" else "🔴"

    msg = f"""
🚧 LIVE SIGNAL

💷 {pair}

Entry⏳ {entry_time}
Exit ⏰ {exit_time}

⌚️ {timeframe}

{arrow} {direction}
"""

    send_message(msg)

    return wait_seconds, entry_time

# =====================================
# CHECK REAL RESULT
# =====================================
def check_result(pair, direction, entry_price):

    expiry_price = get_price(pair)

    if expiry_price is None:
        return "UNKNOWN"

    if direction == "CALL":

        if expiry_price > entry_price:
            return "WIN"

        else:
            return "LOSS"

    else:

        if expiry_price < entry_price:
            return "WIN"

        else:
            return "LOSS"

# =====================================
# SEND SUMMARY
# =====================================
def send_summary():

    today = datetime.now(TIMEZONE).strftime("%d/%m/%Y")

    msg = f"""
📊 Summary Date {today}

Total signal given - {total_signals}

Total Win - {wins}

Total Loss - {losses}
"""

    send_message(msg)

# =====================================
# MAIN LOOP
# =====================================
def run():

    global total_signals
    global wins
    global losses

    print("🚀 LIVE OTC BOT STARTED")

    while True:

        try:

            signal = generate_signal()

            if signal is None:

                print("NO STRONG SIGNAL")

                time.sleep(15)

                continue

            pair, direction, timeframe = signal

            entry_price = get_price(pair)

            if entry_price is None:

                time.sleep(10)

                continue

            wait_seconds, entry_time = send_signal(
                pair,
                direction,
                timeframe,
                entry_price
            )

            # WAIT FOR TRADE EXPIRY
            time.sleep(wait_seconds)

            # REAL RESULT CHECK
            result = check_result(
                pair,
                direction,
                entry_price
            )

            total_signals += 1

            if result == "WIN":
                wins += 1
                emoji = "✅"

            else:
                losses += 1
                emoji = "❌"

            # SEND RESULT
            result_message = f"""
{emoji} {result} {emoji}

{pair} | ⏰ {entry_time}
"""

            send_message(result_message)

            # SEND SUMMARY
            send_summary()

            # WAIT BEFORE NEXT SIGNAL
            time.sleep(15)

        except Exception as e:

            print("MAIN ERROR:", e)

            time.sleep(10)

# =====================================
# START BOT
# =====================================
if __name__ == "__main__":
    run()
