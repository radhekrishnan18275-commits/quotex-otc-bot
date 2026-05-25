import os
import asyncio
import yfinance as yf
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from telegram import Bot
from datetime import datetime, timedelta
import pytz

# =========================
# TELEGRAM SETTINGS
# =========================

BOT_TOKEN = os.getenv("8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0")
CHAT_ID = os.getenv("8241640506")

bot = Bot(token=BOT_TOKEN)

# =========================
# INDIA TIME
# =========================

IST = pytz.timezone("Asia/Kolkata")

# =========================
# FOREX PAIRS
# =========================

LIVE_PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "EURGBP": "EURGBP=X",
    "EURJPY": "EURJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDJPY": "JPY=X",
    "USDCAD": "CAD=X",
    "GBPJPY": "GBPJPY=X",
    "NZDUSD": "NZDUSD=X"
}

# =========================
# SIGNAL CHECK
# =========================

def get_signal(symbol):

    try:

        data = yf.download(
            symbol,
            period="1d",
            interval="1m",
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            return None

        close = data["Close"].squeeze()

        ema9 = EMAIndicator(close=close, window=9).ema_indicator()
        ema21 = EMAIndicator(close=close, window=21).ema_indicator()

        rsi = RSIIndicator(close=close, window=14).rsi()

        macd = MACD(close=close)

        macd_line = macd.macd()
        macd_signal = macd.macd_signal()

        # BUY
        if (
            ema9.iloc[-1] > ema21.iloc[-1]
            and rsi.iloc[-1] > 55
            and macd_line.iloc[-1] > macd_signal.iloc[-1]
        ):

            return "UP"

        # SELL
        elif (
            ema9.iloc[-1] < ema21.iloc[-1]
            and rsi.iloc[-1] < 45
            and macd_line.iloc[-1] < macd_signal.iloc[-1]
        ):

            return "DOWN"

        return None

    except Exception as e:

        print(f"ERROR: {e}")
        return None

# =========================
# SEND TELEGRAM SIGNAL
# =========================

async def send_signal(pair, direction):

    now = datetime.now(IST)

    signal_time = now.strftime("%I:%M:%S %p")

    entry_time_dt = now + timedelta(minutes=2)
    expiry_time_dt = entry_time_dt + timedelta(minutes=5)

    entry_time = entry_time_dt.strftime("%I:%M %p")
    expiry_time = expiry_time_dt.strftime("%I:%M %p")

    message = f'''
📊 Asset : {pair}

🕒 Signal Time : {signal_time}

⏰ Entry Time : {entry_time}

⌛ Expiry Time : {expiry_time}

📈 Direction : {direction} {'⬆️' if direction == 'UP' else '⬇️'}

🔥 Accuracy : HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation
'''

    await bot.send_message(chat_id=CHAT_ID, text=message)

    print(f"SIGNAL SENT: {pair} {direction}")

    await asyncio.sleep(300)

    result = f'''
🏁 Trade Finished

📊 Pair : {pair}

📈 Direction : {direction}

⌛ Expiry : Completed

✅ Check Quotex Result
'''

    await bot.send_message(chat_id=CHAT_ID, text=result)

# =========================
# MAIN LOOP
# =========================

async def run_bot():

    print("================================")
    print("LIVE FOREX BOT STARTED")
    print("================================")

    while True:

        found = False

        for pair, symbol in LIVE_PAIRS.items():

            signal = get_signal(symbol)

            if signal:

                found = True

                await send_signal(pair, signal)

                break

        if not found:
            print("NO STRONG SIGNAL FOUND")

        await asyncio.sleep(60)

# =========================
# START BOT
# =========================

asyncio.run(run_bot())
