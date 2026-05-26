import os
from flask import Flask, request
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    signal = data.get("signal")
    symbol = data.get("symbol", "UNKNOWN")

    if signal == "BUY":
        msg = f"🟢 BUY SIGNAL\nSymbol: {symbol}"
    elif signal == "SELL":
        msg = f"🔴 SELL SIGNAL\nSymbol: {symbol}"
    else:
        msg = f"⚠ UNKNOWN SIGNAL: {data}"

    bot.send_message(chat_id=CHAT_ID, text=msg)

    return "ok"

@app.route("/")
def home():
    return "Telegram Signal Bot Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
