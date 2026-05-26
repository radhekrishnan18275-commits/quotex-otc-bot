import os
import asyncio
from flask import Flask, request
from telegram import Bot

# -----------------------
# ENV VARIABLES
# -----------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise Exception("BOT_TOKEN or CHAT_ID missing")

# -----------------------
# FLASK APP
# -----------------------
app = Flask(__name__)

# -----------------------
# TELEGRAM BOT
# -----------------------
bot = Bot(token=BOT_TOKEN)

# -----------------------
# SEND TELEGRAM MESSAGE
# -----------------------
async def send_telegram_message(message):
    await bot.send_message(chat_id=CHAT_ID, text=message)

# -----------------------
# HOME ROUTE
# -----------------------
@app.route("/")
def home():
    return "Bot is running 🚀"

# -----------------------
# WEBHOOK ROUTE
# -----------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("DATA RECEIVED:", data)

        signal = data.get("signal", "UNKNOWN")
        symbol = data.get("symbol", "UNKNOWN")

        if signal == "BUY":
            msg = f"🟢 BUY SIGNAL\nSymbol: {symbol}"

        elif signal == "SELL":
            msg = f"🔴 SELL SIGNAL\nSymbol: {symbol}"

        else:
            msg = f"⚠ SIGNAL RECEIVED\n{data}"

        print("SENDING MESSAGE:", msg)
        print("CHAT ID:", CHAT_ID)

        asyncio.run(send_telegram_message(msg))

        print("MESSAGE SENT SUCCESS")

        return "OK", 200

    except Exception as e:
        print("FULL ERROR:", e)
        return "ERROR", 500

# -----------------------
# START SERVER
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
