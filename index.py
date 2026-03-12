from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from config import BOT_TOKEN
import json
import os

USERS_FILE = "users.json"

# --- Foydalanuvchilarni yuklash ---
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

# --- Foydalanuvchi qo‘shilganda saqlash funksiyasi ---
def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# --- Doska boshlang'ich holati ---
doska = {
    "red": None,     # 🔴 qizil odam
    "yellow": [],    # 🟡 sariq odamlar
    "blue": [],      # 🔵 ko‘k odamlar
    "white": []      # ⚪ yangi kelganlar
}

# --- Slaydlar matni ---
slides = [
    "🎁 Slayd 1:\n\nBu bot Dori Poluchay loyihasining O‘zbekcha versiyasi. Siz referal orqali qo‘shilasiz.",
    "🎁 Slayd 2:\n\nOq qatorda yangi kelganlar joylashadi. Qizil odamga to‘lov yuborish talab qilinadi.",
    "🎁 Slayd 3:\n\nSariq va ko‘k qatorda yetakchilar va quruvchilar joylashadi.",
    "🎁 Slayd 4:\n\nPul to‘lovlarini faqat qizil odam tasdiqlaydi.",
    "✅ Slayd 5:\n\nAgar barcha shartlarni tushundingiz, oxirida 'Men shartlarga roziman' tugmasini bosing."
]

# --- Doskani vizualizatsiya qilish ---
def doska_korish(doska):
    text = ""
    text += f"Qizil: 🔴 {doska['red']}\n" if doska['red'] else "Qizil: bo'sh\n"
    text += "Sariq: " + "  ".join([f"🟡 {u}" for u in doska['yellow']]) + "\n" if doska['yellow'] else "Sariq: bo'sh\n"
    text += "Ko‘k: " + "  ".join([f"🔵 {u}" for u in doska['blue']]) + "\n" if doska['blue'] else "Ko‘k: bo'sh\n"
    text += "Oq: " + "  ".join([f"⚪ {u}" for u in doska['white']]) + "\n" if doska['white'] else "Oq: bo'sh\n"
    return text

async def doska_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = doska_korish(doska)
    await update.message.reply_text(text)

    # --- /info komandasi ---
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Bu bot Dori Poluchay loyihasining O‘zbekcha versiyasi.\n\n"
        "🔹 Foydalanuvchilar referal orqali qo‘shiladi.\n"
        "🔹 Yangi foydalanuvchilar oq qatorda joylashadi.\n"
        "🔹 Qizil odam pullarni oladi va yangi qatorda joylashishni tasdiqlaydi.\n"
        "🔹 Doska orqali qizil, sariq, ko‘k va oq qatorlarni kuzatishingiz mumkin.\n\n"
        "Siz loyihaga qo‘shilishdan oldin slaydlar orqali shartlar bilan tanishishingiz va tasdiqlashingiz kerak."
    )

    # --- /help komandasi ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📜 Bot komandalar ro‘yxati:\n\n"
        "/start - botni boshlash va slaydlar orqali shartlarga rozilik\n"
        "/help - yordam, komandalar ro‘yxati\n"
        "/info - loyiha haqida ma’lumot\n"
        "/ref <referal_id> - referal orqali loyihaga qo‘shilish\n"
        "/tolov - qizil odamga to‘lov ko‘rsatish\n"
        "/doska - oq/sariq/ko‘k/qizil qatordagi foydalanuvchilar\n"
        "/myref - o‘z referal ID’ingizni ko‘rish\n"
    )

# --- /start komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.full_name

    # Foydalanuvchi birinchi marta qo‘shilsa
    if user_id not in users:
        users[user_id] = {"name": username, "referal": None, "position": None, "level": 1, "agreed": False}
        save_users()

    # Agar birinchi foydalanuvchi bo‘lsa, avtomatik qizilga qo‘shiladi
    if doska["red"] is None:
        doska["red"] = username
        await update.message.reply_text(
            f"Salom {username}! Siz loyihaga birinchi bo‘lib qo‘shildingiz va QIZIL odam bo‘ldingiz.\n"
            f"Sizning referal ID’ingiz: {user_id}\n"
            "Endi siz boshqa odamlarni loyihaga qo‘shishingiz mumkin."
        )
        return

    # Slaydni boshlash
    await send_slide(update, 0)

# --- Slaydlarni yuborish funksiyasi ---
async def send_slide(update: Update, slide_index: int):
    user_id = str(update.effective_user.id)
    if slide_index >= len(slides):
        return

    keyboard = []
    if slide_index == len(slides) - 1:
        keyboard = [[InlineKeyboardButton("Men shartlarga roziman ✅", callback_data=f"agree")]]
    else:
        keyboard = [[InlineKeyboardButton("Keyingi ➡️", callback_data=f"slide_{slide_index + 1}")]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(slides[slide_index], reply_markup=reply_markup)

# --- Callback handler slaydlar uchun ---
async def slide_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if data.startswith("slide_"):
        slide_index = int(data.split("_")[1])
        await send_slide(query, slide_index)
    elif data == "agree":
        users[user_id]["agreed"] = True
        save_users()
        await query.edit_message_text(
            "Siz barcha shartlarni tushundingiz va rozi bo‘ldingiz.\n"
            "Endi referal orqali loyihaga qo‘shilishingiz mumkin: /ref <referal_id>"
        )

# --- Foydalanuvchini qo‘shish funksiyasi ---
def qoshuvchi(doska, user, referal_tomoni):
    if len(doska["white"]) >= 8:
        ajralish(doska)
    if referal_tomoni == "left":
        doska["white"].insert(0, user)
    else:
        doska["white"].append(user)
    return doska

def ajralish(doska):
    left = doska["white"][:4]
    right = doska["white"][4:8]

    if len(left) == 4:
        doska["blue"].extend(left[:2])
        doska["yellow"].extend(left[2:])
        doska["white"] = doska["white"][4:]

    if len(right) == 4:
        doska["blue"].extend(right[:2])
        doska["yellow"].extend(right[2:])
        doska["white"] = doska["white"][:4]

    if doska["yellow"]:
        doska["red"] = doska["yellow"].pop(0)

# --- /ref komandasi ---
async def ref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.full_name
    args = context.args

    if user_id not in users:
        await update.message.reply_text("Avvalo /start orqali botni ishga tushiring va shartlarga rozi bo‘ling.")
        return

    if not users[user_id]["agreed"]:
        await update.message.reply_text("Avvalo barcha slaydlarni ko‘rib 'Men shartlarga roziman' tugmasini bosing.")
        return

    if not args:
        await update.message.reply_text("Iltimos, referal ID kiriting: /ref <referal_id>")
        return

    referal_id = str(args[0])
    if referal_id not in users:
        await update.message.reply_text("Noto‘g‘ri referal ID yoki foydalanuvchi mavjud emas.")
        return

    users[user_id]["referal"] = referal_id

    left_space = 4 - len(doska["white"][:4])
    right_space = 4 - len(doska["white"][4:8])
    referal_tomoni = "left" if left_space >= right_space else "right"

    qoshuvchi(doska, username, referal_tomoni)

    await update.message.reply_text(
        f"Siz loyihaga qo‘shildingiz! Sizning referalingiz: {users[referal_id]['name']}"
    )
    save_users()

# --- To‘lovni ko‘rsatish komandasi ---
async def tolov(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if doska["red"]:
        await update.message.reply_text(f"Pulni quyidagi qizil odamga yuboring: @{doska['red']}")
    else:
        await update.message.reply_text("Hozir qizil odam yo‘q.")

# --- /myref komandasi ---
async def myref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in users:
        await update.message.reply_text(
            f"Sizning referal ID’ingiz: {user_id}\n"
            "Siz bu ID’ni boshqa odamlar bilan bo‘lishib, loyihaga qo‘shilishini ta’minlashingiz mumkin."
        )
    else:
        await update.message.reply_text(
            "Siz hali loyihaga qo‘shilmadingiz. Avvalo /start va /ref orqali qo‘shiling."
        )

# --- Botni ishga tushirish ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("info", info))
app.add_handler(CommandHandler("ref", ref))
app.add_handler(CommandHandler("tolov", tolov))
app.add_handler(CommandHandler("doska", doska_command))
app.add_handler(CommandHandler("myref", myref))
app.add_handler(CallbackQueryHandler(slide_callback))  # slaydlar tugmalari

print("Bot ishga tushdi...")
app.run_polling()