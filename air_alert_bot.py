import requests
import time
import os
from telegram import Bot
from datetime import datetime

# ⏱ Період перевірки (в секундах)
CHECK_INTERVAL = 60

# 🔐 Змінні оточення
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

bot = Bot(token=BOT_TOKEN)

# 🌐 API джерела
API_URL = "https://alerts.com.ua/api/states"  # Отримання статусів тривог по регіонах

# 📦 Стан тривог на попередньому кроці
last_alerted_regions = set()

def fetch_air_alerts():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise TypeError(f"Очікувався список, але отримано {type(data).__name__}")

        active_regions = [entry["name"] for entry in data if entry.get("active")]
        return set(active_regions)

    except Exception as e:
        bot.send_message(chat_id=CHANNEL_ID, text=f"❌ Помилка при перевірці тривог: {e}")
        return None

def format_alert_message(active_regions):
    if not active_regions:
        return "✅ Все спокійно."
    return "🚨 Повітряна тривога у: " + ", ".join(active_regions)

def main():
    global last_alerted_regions
    while True:
        active_regions = fetch_air_alerts()

        if active_regions is not None and active_regions != last_alerted_regions:
            message = format_alert_message(active_regions)
            bot.send_message(chat_id=CHANNEL_ID, text=message)
            last_alerted_regions = active_regions

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
