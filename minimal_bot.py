# minimal_bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from tinydb import TinyDB, Query

db = TinyDB('users.json')
User = Query()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.search(User.id == user_id):
        db.insert({'id': user_id, 'status': 'new'})
        await update.message.reply_text(f"Salom! Siz ro‘yxatdan o‘tdingiz. ID: {user_id}")
    else:
        await update.message.reply_text("Siz allaqachon ro‘yxatdan o‘tgansiz.")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Sizning ID’ingiz: {update.effective_user.id}")

async def board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.all()
    text = "Hozirgi foydalanuvchilar:\n"
    for u in users:
        text += f"ID: {u['id']} | Status: {u['status']}\n"
    await update.message.reply_text(text)

if __name__ == "__main__":
    app = ApplicationBuilder().token("8729579755:AAEczdKOLm1lbjQmKArRbTBpo_4mLZbOQVo").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("board", board))
    print("Bot ishga tushdi...")
    app.run_polling()