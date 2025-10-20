import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7846824717:AAExOg9tnsUxfzRqw2jLCd4xfN0OcaOEdUE"
WEBAPP_URL = "https://bov-token-copy-7e0fbdcc.base44.app"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kb = [[KeyboardButton("🎮 Oyunu Aç", web_app=WebAppInfo(url=WEBAPP_URL))]]
    reply_markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    await update.message.reply_text(
        f"Merhaba {user.first_name or 'Oyuncu'} 👋\n"
        "Aşağıdaki butona tıklayarak oyunu hemen Telegram içinde açabilirsin 🎯",
        reply_markup=reply_markup
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

asyncio.run(app.run_polling())
