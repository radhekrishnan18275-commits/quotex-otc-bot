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
