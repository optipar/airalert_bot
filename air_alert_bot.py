import os
import time
import requests
from telegram import Bot

# Читання змінних середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# Ініціалізація збереженого стану
last_state = None

def check_alerts():
    try:
        url = "https://alerts.com.ua/api/states"
        response = requests.get(url)
        data = response.json()

        # Отримати список областей, де тривога
        active = [region['name'] for region in data if region['alert']]

        if active:
            return f"🚨 Повітряна тривога у: {', '.join(active)}"
        else:
            return "✅ Все спокійно."
    except Exception as e:
        return f"❌ Помилка при перевірці тривог: {e}"

while True:
    try:
        message = check_alerts()
        if message != last_state:
            bot.send_message(chat_id=CHAT_ID, text=message)
            last_state = message
    except Exception as e:
        print(f"Помилка при надсиланні повідомлення: {e}")
    
    time.sleep(60)  # Чекати 60 сек перед новою перевіркою
