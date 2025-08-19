import os
import time
import requests
import asyncio
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

last_state = None

def check_alerts():
    try:
        response = requests.get("https://alerts.com.ua/api/states")
        response.raise_for_status()  # якщо HTTP помилка
        data = response.json()

        if not isinstance(data, list):
            raise ValueError("Очікувався список, але отримано щось інше.")

        active = [region['name'] for region in data if region.get('alert')]
        if active:
            return f"🚨 Повітряна тривога у: {', '.join(active)}"
        else:
            return "✅ Все спокійно."

    except Exception as e:
        print(f"[ERROR] {e}")
        try:
            print("Вміст відповіді:", response.text)
        except:
            pass
        return f"❌ Помилка при перевірці тривог: {e}"

async def main():
    global last_state
    while True:
        message = check_alerts()
        if message != last_state:
            try:
                await bot.send_message(chat_id=CHAT_ID, text=message)
                last_state = message
            except Exception as e:
                print(f"[SEND ERROR] {e}")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
