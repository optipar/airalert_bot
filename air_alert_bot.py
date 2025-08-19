import os
import time
import requests
import asyncio
from datetime import datetime
from telegram import Bot, InputFile

# Змінні середовища (налаштуй у Railway або .env)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID або @назва_каналу
bot = Bot(token=BOT_TOKEN)

# URL API
REGIONS_API_URL = "https://alerts.com.ua/api/regions"
MAP_IMAGE_URL = "https://alerts.in.ua/static/img/map.png"

# Стан останнього повідомлення
last_alert_message = None

def get_formatted_time():
    return datetime.now().strftime("%H:%M")

async def check_alerts():
    global last_alert_message
    try:
        # Отримуємо JSON
        response = requests.get(REGIONS_API_URL)
        data = response.json()

        # Якщо прийшов dict, а не list — повертаємо помилку
        if isinstance(data, dict):
            raise TypeError("Очікувався список, але отримано dict")

        # Створюємо список тривог
        alerts = []
        for region in data:
            region_name = region["name"]
            if region.get("alerts"):
                alerts.append(f"🔴 {get_formatted_time()} Повітряна тривога в {region_name}")

            for area in region.get("areas", []):
                if area.get("alert"):
                    alerts.append(f"🔴 {get_formatted_time()} Повітряна тривога в {area['name']}")

        # Якщо немає тривог
        if not alerts:
            message = f"✅ Все спокійно. {get_formatted_time()}"
            if message != last_alert_message:
                await bot.send_message(chat_id=CHAT_ID, text=message)
                last_alert_message = message
            return

        # Формуємо повідомлення
        caption = "\n".join(alerts)
        if caption == last_alert_message:
            return  # Не надсилаємо дубль

        # Завантажуємо карту
        img = requests.get(MAP_IMAGE_URL)
        with open("map.png", "wb") as f:
            f.write(img.content)

        # Надсилаємо фото з підписом
        with open("map.png", "rb") as photo:
            await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=caption)

        last_alert_message = caption

    except Exception as e:
        error_message = f"❌ Помилка при перевірці тривог: {e}"
        if error_message != last_alert_message:
            await bot.send_message(chat_id=CHAT_ID, text=error_message)
            last_alert_message = error_message

async def main():
    while True:
        await check_alerts()
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
