import os, sqlite3, asyncio, nest_asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

nest_asyncio.apply()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@TradingBot"
CHANNEL_INVITE_LINK = "https://t.me/+HKZpb8KyqVdiNDMy"
ADMIN_IDS = [5257805935]
DB_PATH = "users.db"

# ====== База данных ======
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            is_subscribed INTEGER DEFAULT 0,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_or_update_user(user, is_sub=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users(user_id, username, first_name, last_name, is_subscribed, last_seen)
        VALUES(?,?,?,?,?,CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
        username=excluded.username, first_name=excluded.first_name,
        last_name=excluded.last_name, is_subscribed=excluded.is_subscribed,
        last_seen=CURRENT_TIMESTAMP
    """, (user.id, user.username, user.first_name, user.last_name, int(is_sub)))
    conn.commit()
    conn.close()

async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except BadRequest:
        return False

def user_is_admin(uid): return uid in ADMIN_IDS

# ====== Хендлеры ======
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sub = await is_subscribed(ctx.bot, user.id)
    add_or_update_user(user, sub)
    if sub:
        await update.message.reply_text(f"🌙 Привет, {user.first_name}! Доступ открыт.")
    else:
        kb = [[InlineKeyboardButton("📈 Подписаться", url=CHANNEL_INVITE_LINK)],
              [InlineKeyboardButton("Проверить подписку", callback_data="check_sub")]]
        await update.message.reply_text("Подпишись на канал, чтобы пользоваться ботом:", reply_markup=InlineKeyboardMarkup(kb))

async def check(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    if await is_subscribed(ctx.bot, user.id):
        add_or_update_user(user, True)
        await q.edit_message_text("✅ Подписка подтверждена, можешь пользоваться ботом.")
    else:
        kb = [[InlineKeyboardButton("📈 Подписаться", url=CHANNEL_INVITE_LINK)],
              [InlineKeyboardButton("Проверить снова", callback_data="check_sub")]]
        await q.edit_message_text("❌ Подписка не найдена. Попробуй снова:", reply_markup=InlineKeyboardMarkup(kb))

# ====== Статистика ======
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM users WHERE is_subscribed=1")
    subs = cur.fetchone()[0]
    since = datetime.utcnow() - timedelta(days=1)
    cur.execute("SELECT COUNT(*) FROM users WHERE first_seen>=?", (since,))
    new_24h = cur.fetchone()[0]
    conn.close()
    return {"total": total, "subscribed": subs, "new_24h": new_24h}

async def admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    if not user_is_admin(u.id):
        return await update.message.reply_text("🚫 Нет доступа")
    kb = [[InlineKeyboardButton("📊 Статистика", callback_data="adm_stats")],
          [InlineKeyboardButton("📥 Экспорт CSV", callback_data="adm_export")]]
    await update.message.reply_text("Панель администратора:", reply_markup=InlineKeyboardMarkup(kb))

async def adm_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    u = q.from_user
    if not user_is_admin(u.id):
        return await q.edit_message_text("🚫 Нет доступа")
    if q.data == "adm_stats":
        st = get_stats()
        await q.edit_message_text(f"📊 Пользователей: {st['total']}\nПодписаны: {st['subscribed']}\nНовых за 24ч: {st['new_24h']}")
    elif q.data == "adm_export":
        import tempfile, csv
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        conn.close()
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        writer = csv.writer(tmp)
        writer.writerow(["id","uid","username","first","last","sub","first_seen","last_seen"])
        writer.writerows(rows)
        tmp.close()
        await ctx.bot.send_document(chat_id=u.id, document=tmp.name, filename="users.csv")

# ====== Основной запуск ======
async def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check, pattern="check_sub"))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(adm_cb, pattern="adm_"))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
