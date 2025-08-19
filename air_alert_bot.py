import os
import asyncio
import logging
import aiohttp
from datetime import datetime
from telegram import Bot

# Змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API
API_URL = "https://alerts.com.ua/api/states"
UPDATE_INTERVAL = 60  # перевірка кожні 60 секунд

# Словник для збереження попереднього стану
previous_state = {}

async def fetch_data():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"❌ Помилка HTTP: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"❌ Помилка при запиті до API: {e}")
        return None

def parse_alerts(data):
    if not isinstance(data, dict):
        raise ValueError(f"Очікувався dict, отримано: {type(data)}")

    alerts = []
    for region_code, info in data.items():
        if not isinstance(info, dict):
            continue

        name = info.get("name")
        alert = info.get("alert", False)

        if name and alert:
            alerts.append(name)

    return alerts

async def send_message(bot: Bot, message: str):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=message)
    except Exception as e:
        logger.error(f"❌ Помилка при надсиланні повідомлення: {e}")

async def main_loop():
    global previous_state
    bot = Bot(token=BOT_TOKEN)
    logger.info("🚀 Бот запущено!")

    while True:
        try:
            data = await fetch_data()
            if data is None:
                await send_message(bot, "❌ Не вдалося отримати дані з API.")
                await asyncio.sleep(UPDATE_INTERVAL)
                continue

            try:
                current_alerts = parse_alerts(data)
            except Exception as e:
                await send_message(bot, f"❌ Помилка при перевірці тривог: {e}")
                await asyncio.sleep(UPDATE_INTERVAL)
                continue

            # Порівняння зі старим станом
            current_alerts_set = set(current_alerts)
            previous_alerts_set = set(previous_state.get("alerts", []))

            if current_alerts_set != previous_alerts_set:
                if current_alerts:
                    region_list = ", ".join(current_alerts)
                    await send_message(bot, f"🚨 Повітряна тривога у: {region_list}")
                else:
                    await send_message(bot, "✅ Усі області без тривог.")
                previous_state["alerts"] = current_alerts

        except Exception as e:
            logger.error(f"❌ Загальна помилка: {e}")
            await send_message(bot, f"❌ Загальна помилка: {e}")

        await asyncio.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main_loop())
