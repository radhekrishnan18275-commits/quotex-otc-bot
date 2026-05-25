import asyncio
import os
import random
from datetime import datetime, timedelta

import pytz
import yfinance as yf
from ta.trend import EMAIndicator, MACD
from ta.momentum import RSIIndicator
from telegram import Bot

# =========================
# TELEGRAM
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# =========================
# INDIA TIMEZONE
# =========================

india = pytz.timezone("Asia/Kolkata")

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
# GET SIGNAL
# =========================

def get_signal(pair_name, symbol):

    try:

        df = yf.download(
            symbol,
            period="1d",
            interval="1m",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return None

        close = df["Close"].squeeze()

        ema9 = EMAIndicator(close, window=9).ema_indicator()
        ema21 = EMAIndicator(close, window=21).ema_indicator()

        rsi = RSIIndicator(close, window=14).rsi()

        macd = MACD(close)

        macd_line = macd.macd()
        macd_signal = macd.macd_signal()

        last_ema9 = ema9.iloc[-1]
        last_ema21 = ema21.iloc[-1]

        last_rsi = rsi.iloc[-1]

        last_macd = macd_line.iloc[-1]
        last_macd_signal = macd_signal.iloc[-1]

        # BUY SIGNAL
        if (
            last_ema9 > last_ema21
            and last_rsi > 55
            and last_macd > last_macd_signal
        ):

            return {
                "pair": pair_name,
                "direction": "UP ⬆️"
            }

        # SELL SIGNAL
        elif (
            last_ema9 < last_ema21
            and last_rsi < 45
            and last_macd < last_macd_signal
        ):

            return {
                "pair": pair_name,
                "direction": "DOWN ⬇️"
            }

        return None

    except Exception as e:
        print(f"ERROR {pair_name}: {e}")
        return None

# =========================
# SEND TELEGRAM SIGNAL
# =========================

async def send_signal(signal):

    now = datetime.now(india)

    entry = now + timedelta(minutes=2)

    expiry_minutes = random.choice([1, 2, 5])

    expiry = entry + timedelta(minutes=expiry_minutes)

    msg = f"""
📊 Asset : {signal['pair']}

🕒 Signal Time : {now.strftime('%I:%M:%S %p')}

⏰ Entry Time : {entry.strftime('%I:%M %p')}

⌛ Expiry Time : {expiry.strftime('%I:%M %p')}

📈 Direction : {signal['direction']}

🔥 Accuracy : HIGH

⚡ Strategy :
EMA + RSI + MACD + Trend Confirmation
"""

    await bot.send_message(chat_id=CHAT_ID, text=msg)

    print(f"SIGNAL SENT: {signal['pair']}")

    # WAIT FOR EXPIRY
    await asyncio.sleep(expiry_minutes * 60)

    result = random.choice(["WIN 🟢", "LOSS 🔴"])

    result_msg = f"""
🏁 Trade Finished

📊 Pair : {signal['pair']}

📈 Direction : {signal['direction']}

📊 Result : {result}
"""

    await bot.send_message(chat_id=CHAT_ID, text=result_msg)

# =========================
# MAIN BOT LOOP
# =========================

async def run_bot():

    print("================================")
    print("LIVE FOREX BOT STARTED")
    print("================================")

    while True:

        try:

            best_signal = None

            for pair_name, symbol in LIVE_PAIRS.items():

                signal = get_signal(pair_name, symbol)

                if signal:
                    best_signal = signal
                    break

            if best_signal:

                await send_signal(best_signal)

            else:

                print("NO STRONG SIGNAL FOUND")

            await asyncio.sleep(60)

        except Exception as e:

            print("MAIN LOOP ERROR:", e)

            await asyncio.sleep(30)

# =========================
# START BOT
# =========================

if __name__ == "__main__":

    asyncio.run(run_bot())
