import os
import requests
import time
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://www.ukrainealarm.com/api/v1/alerts/active"

bot = Bot(token=TOKEN)

def check_alerts():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200 and response.json():
            bot.send_message(chat_id=CHAT_ID, text="🚨 Повітряна тривога в Україні!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        check_alerts()
        time.sleep(60)
