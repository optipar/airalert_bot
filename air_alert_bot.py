import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# === Flask для Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Air Alert Bot is running."

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# === Telegram-бот ===

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Зберігай токен в ENV-перемінній у Render

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт! Бот працює та слухає повітряні тривоги.")

def run_telegram_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

# === Запуск ===
if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    run_telegram_bot()
