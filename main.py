import logging
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# SheetDB API URL-lari
API_LINKS = [
    {
        "Xodimlar": "https://sheetdb.io/api/v1/wjt0stvxvhv1u?sheet=Xodimlar",
        "Maoshlar": "https://sheetdb.io/api/v1/wjt0stvxvhv1u?sheet=Maoshlar"
    },
    {
        "Xodimlar": "https://sheetdb.io/api/v1/xcez74sjvsjc4?sheet=Xodimlar",
        "Maoshlar": "https://sheetdb.io/api/v1/xcez74sjvsjc4?sheet=Maoshlar"
    }
]

# Log sozlamasi
logging.basicConfig(level=logging.INFO)

# Bosqichlar
LOGIN, PAROL = range(2)

# Foydalanuvchi ma'lumotlari vaqtincha saqlanadi
user_data = {}

def request_with_fallback(url):
    """API-ga so‘rov yuboradi va agar birinchi URL ishlamasa, ikkinchisiga o'tadi."""
    for link in API_LINKS:
        response = requests.get(link[url])
        if response.status_code == 200:
            return response.json()
    return None

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Ro'yxatdan o'tish uchun iltimos login (ID) kiriting:")
    return LOGIN

# Login (ID) qabul qilinadi
async def login_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {"ID": update.message.text}
    await update.message.reply_text("Parolingizni kiriting:")
    return PAROL

# Parol qabul qilinadi va tekshiriladi
async def parol_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    parol = update.message.text
    login = user_data[user_id]["ID"]

    data = request_with_fallback("Xodimlar")
    if data is None:
        await update.message.reply_text("Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        return ConversationHandler.END

    for row in data:
        if row.get("ID") == login and row.get("Parol") == parol:
            ism = row.get("Ism")
            update_url = f"https://sheetdb.io/api/v1/wjt0stvxvhv1u/ID/{login}"
            update_payload = {"data": {"Telegram_ID": str(user_id)}}
            update_response = requests.patch(update_url, json=update_payload)

            if update_response.status_code in [200, 201]:
                keyboard = [[KeyboardButton("📊 Maoshim")]]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                await update.message.reply_text(
                    f"<b>{ism}</b>, siz ro'yxatdan muvoffaqiyatli o'tdingiz!\n"
                    "Endi har oy maoshingizni onlayn ko'rib borishingiz mumkin! ✅",
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("Xatolik yuz berdi. Iltimos, qaytadan urinib ko‘ring.")
            return ConversationHandler.END

    await update.message.reply_text("❌ Login yoki parol noto‘g‘ri. Qaytadan urinib ko‘ring.")
    return LOGIN

# 📊 Maoshim komandasi
async def maoshim_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    data = request_with_fallback("Maoshlar")
    if data is None:
        await update.message.reply_text("Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        return

    for row in data:
        if row.get("Telegram_ID") == user_id:
            ism = row.get("F.I.O")
            id_ = row.get("ID")
            jami = row.get("Jami") or "0"

            # Maosh bo‘limlarini ajratib olish
            markaz_fiks = int(row.get("Markaz Fiks") or 0)
            markaz_kpi = int(row.get("Markaz KPI") or 0)
            bonus = int(row.get("Markaz Bonus") or 0)
            avans = int(row.get("Markaz Avans") or 0)
            soliq = int(row.get("Markaz Soliq") or 0)
            plastikka = int(row.get("Markaz Plastikka") or 0)
            beriladi = int(row.get("Markaz Beriladi") or 0)

            maktab_fiks = int(row.get("Maktab Fiks") or 0)
            maktab_kpi = int(row.get("Maktab KPI") or 0)
            maktab_avans = int(row.get("Maktab Avans") or 0)
            maktab_soliq = int(row.get("Maktab Soliq") or 0)
            maktab_plastikka = int(row.get("Maktab Plastikka") or 0)
            maktab_beriladi = int(row.get("Maktab Beriladi") or 0)
            hisoblangan = int(row.get("Hisoblangan") or 0)

            text = (
                f"👨‍💼 <b>Ism:</b> {ism}\n"
                f"🆔 <b>ID:</b> {id_}\n\n"
                f"🏢 <b>Markaz:</b>\n"
                f"- Fiks: {markaz_fiks:,}\n"
                f"- KPI: {markaz_kpi:,}\n"
                f"- Bonus: {bonus:,}\n"
                f"- Avans: {avans:,}\n"
                f"- Soliq: {soliq:,}\n"
                f"- Plastikka: {plastikka:,}\n"
                f"- Beriladi: {beriladi:,}\n\n"
                f"🏫 <b>Maktab:</b>\n"
                f"- Fiks: {maktab_fiks:,}\n"
                f"- KPI: {maktab_kpi:,}\n"
                f"- Avans: {maktab_avans:,}\n"
                f"- Soliq: {maktab_soliq:,}\n"
                f"- Plastikka: {maktab_plastikka:,}\n"
                f"- Beriladi: {maktab_beriladi:,}\n\n"
                f"💵 <b>Hisoblangan: {int(hisoblangan):,} so'm</b> \n"
                f"💵 <b>Jami maosh:</b> {int(jami):,} so'm"
            ).replace(",", " ")

            await update.message.reply_text(text, parse_mode="HTML")
            return

    await update.message.reply_text("Siz ro'yxatdan o'tmagansiz yoki ma'lumot topilmadi.")

# /cancel komandasi
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ro'yxatdan o'tish bekor qilindi.")
    return ConversationHandler.END

# Botni ishga tushirish
def main():
    app = ApplicationBuilder().token("8035553721:AAGzJrhIgPlVqwRS_vqc883dbD0Uzghisik").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_handler)],
            PAROL: [MessageHandler(filters.TEXT & ~filters.COMMAND, parol_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(📊 Maoshim)$"), maoshim_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
