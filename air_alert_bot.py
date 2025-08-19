import asyncio
import aiohttp
import os
from flask import Flask
from telegram import Bot
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

API_URL = "https://alerts.com.ua/api/states"  # актуальна перевірена API
CHECK_INTERVAL = 60  # секунд

last_alerts = set()


async def fetch_alerts():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                if response.status != 200:
                    raise Exception(f"Помилка при отриманні даних: {response.status}")
                return await response.json()
    except Exception as e:
        await bot.send_message(chat_id=CHANNEL_ID, text=f"❌ Помилка при перевірці тривог: {e}")
        return None


def format_alert_message(regions):
    now = datetime.now().strftime("%H:%M:%S")
    regions_str = ', '.join(regions)
    return f"🚨 Повітряна тривога у: {regions_str} ⏰ {now}"


async def check_alerts():
    global last_alerts
    data = await fetch_alerts()
    if not data:
        return

    active_regions = [region["name"] for region in data if region.get("active")]

    if set(active_regions) != last_alerts:
        last_alerts = set(active_regions)
        if active_regions:
            msg = format_alert_message(active_regions)
        else:
            msg = "✅ Всі області спокійні"
        await bot.send_message(chat_id=CHANNEL_ID, text=msg)


async def scheduler():
    while True:
        await check_alerts()
        await asyncio.sleep(CHECK_INTERVAL)


@app.route("/")
def home():
    return "Air alert bot is running."


def start():
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    start()
