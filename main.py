import time
import requests

BOT_TOKEN = "8954212814:AAHGIp4mxbKbFHn70uulbXGRNcy1ROJhCm0"
CHAT_ID = "8241640506"

def send_message(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

print("BOT STARTED SUCCESSFULLY")

send_message("✅ BOT IS ONLINE")

while True:

    print("BOT RUNNING...")

    time.sleep(30)
