import os
from flask import Flask, request
from telegram import Bot

# -------------------
# ENV VARIABLES
# -------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise Exception("Missing BOT_TOKEN or CHAT_ID in Render Environment Variables")

bot = Bot(token=BOT_TOKEN)

# -------------------
# FLASK APP
# -------------------
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
            msg = f"⚠ INVALID SIGNAL: {data}"

        bot.send_message(chat_id=CHAT_ID, text=msg)

        return "ok", 200

    except Exception as e:
        print("ERROR:", e)
        return "error", 500


# -------------------
# HEALTH CHECK ROUTE (IMPORTANT FOR RENDER)
# -------------------
@app.route("/")
def home():
    return "Bot is running 🚀"


# -------------------
# START SERVER (CRITICAL)
# -------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
