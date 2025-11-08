import os
import asyncio
import time
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import NetworkError, BadRequest

# Apply nest_asyncio for safety on some platforms
nest_asyncio.apply()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # must be set in Render Environment -> BOT_TOKEN
if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN environment variable is not set. Set it in Render (Environment).")
    raise SystemExit(1)

# Simple dark-themed TradingBot with inline menu buttons
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name or "user"
    keyboard = [
        [InlineKeyboardButton("📈 Старт", callback_data="start_work")],
        [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        f"🌙 <b>TradingBot (Dark)</b>\n\n"
        f"Привет, <b>{user}</b>!\n\n"
        "Добро пожаловать. Выбери действие ниже 👇"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "start_work":
        await query.edit_message_text("🚀 Бот готов к работе! Напиши /help чтобы узнать команды.")
    elif query.data == "help":
        help_text = (
            "ℹ️ <b>Помощь TradingBot</b>\n\n"
            "/start — открыть меню\n"
            "/help — показать это сообщение\n\n"
            "Этот бот оформлен в тёмной теме. Для развёртывания в облаке используйте Render.com и укажите переменную окружения BOT_TOKEN."
        )
        await query.edit_message_text(help_text, parse_mode="HTML")
    else:
        await query.edit_message_text("⚠️ Неизвестная команда.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ <b>Помощь TradingBot</b>\n\n"
        "/start — открыть меню\n"
        "/help — показать это сообщение\n\n"
        "Кнопки: 📈 Старт, ℹ️ Помощь"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")

async def main():
    # main loop with resilient reconnects
    while True:
        try:
            app = ApplicationBuilder().token(BOT_TOKEN).build()
            app.add_handler(CommandHandler("start", start_command))
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CallbackQueryHandler(button_handler))
            print("🌙 TradingBot (Dark) starting... (using BOT_TOKEN from env)")
            # run_polling is an async method that will block until stopped
            await app.run_polling()
        except (NetworkError, BadRequest) as e:
            print(f"⚠️ Network/Telegram error: {e}. Reconnecting in 10 seconds...")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}. Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down TradingBot.")