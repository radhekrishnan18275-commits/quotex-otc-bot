import os
import json
from flask import Flask, request
from telegram import Bot

# -------------------
# ENV
# -------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN missing")

bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# -------------------
# WEBHOOK ROUTE
# -------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        signal = data.get("signal")
        symbol = data.get("symbol", "UNKNOWN")

        if signal == "BUY":
            msg = f"🟢 BUY SIGNAL\nSymbol: {symbol}"
        elif signal == "SELL":
            msg = f"🔴 SELL SIGNAL\nSymbol: {symbol}"
        else:
            msg = f"⚠ Unknown signal: {data}"

        bot.send_message(chat_id=CHAT_ID, text=msg)

        return "ok", 200

    except Exception as e:
        print("Error:", e)
        return "error", 500


# -------------------
# HOME ROUTE
# -------------------
@app.route("/")
def home():
    return "TradingView Bot Running 🚀"


# -------------------
# RUN
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
