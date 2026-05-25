import os
import time
import logging
import yfinance as yf
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# -------------------------
# LOGGING
# -------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# -------------------------
# ENV VARIABLES (RENDER SAFE)
# -------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing. Set it in Render Environment Variables.")

# -------------------------
# INIT BOT
# -------------------------
bot = Bot(token=BOT_TOKEN)

# -------------------------
# SIMPLE CACHE (for rate limit control)
# -------------------------
cache = {}
CACHE_TIME = 30  # seconds

def get_price(symbol="EURUSD=X"):
    """Fetch price with caching to avoid Yahoo rate limit"""
    current_time = time.time()

    # return cached if still valid
    if symbol in cache:
        data, timestamp = cache[symbol]
        if current_time - timestamp < CACHE_TIME:
            return data

    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1m")

        if data.empty:
            return "No data"

        price = float(data["Close"].iloc[-1])

        cache[symbol] = (price, current_time)
        time.sleep(1)  # small delay to reduce rate limit

        return price

    except Exception as e:
        logger.error(f"Error fetching price: {e}")
        return "Error fetching data"

# -------------------------
# TELEGRAM COMMANDS
# -------------------------
def start(update, context):
    update.message.reply_text("Bot started successfully 🚀")

def price(update, context):
    symbol = "EURUSD=X"

    if context.args:
        symbol = context.args[0]

    result = get_price(symbol)
    update.message.reply_text(f"{symbol} Price: {result}")

def help_command(update, context):
    update.message.reply_text(
        "/start - Start bot\n"
        "/price EURUSD=X - Get price\n"
    )

# -------------------------
# MAIN FUNCTION
# -------------------------
def main():
    logger.info("Bot is starting...")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    main()
