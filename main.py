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
# /start komandasi (YANGILANGAN)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    # Maoshlar jadvalidan foydalanuvchi bor-yo'qligini tekshir
    data = request_with_fallback("Maoshlar")
    if data is None:
        await update.message.reply_text("Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        return ConversationHandler.END

    # User bor bo'lsa — avtomatik tanib ol
    for row in data:
        if row.get("Telegram_ID") == user_id:
            ism = row.get("F.I.O") or "Xodim"

            keyboard = [
                [KeyboardButton("📊 Maoshim"), KeyboardButton("⚠ Xatolikka ariza"), KeyboardButton("📋 Bo'limlarga murojat")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

            await update.message.reply_text(
                f"👋 Assalomu aleykum, <b>{ism}</b>!\nColba kompaniyasi HR botiga xush kelibsiz! 🎉",
                parse_mode="HTML",
                reply_markup=reply_markup
            )
            return ConversationHandler.END

    # Agar Telegram_ID yo'q bo'lsa — ro'yxatdan o'tkazamiz
    await update.message.reply_text("Assalomu aleykum! Ro'yxatdan o'tish uchun iltimos login (ID) kiriting:")
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
                keyboard = [
                    [KeyboardButton("📊 Maoshim"), KeyboardButton("⚠ Xatolikka ariza"), KeyboardButton("📋 Bo'limlarga murojat")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                await update.message.reply_text(
                    f"<b>{ism}</b>, siz Colba kompaniyasi HR botiga ro'yxatdan muvoffaqiyatli o'tdingiz!\n"
                    "Endi siz kompaniyamiz xodimlari uchun tayyorlangan qulayiklardan foydalanishiz mumkin! ✅",
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
            def to_int(value):
                """Vergullarni olib tashlab, int() ga aylantiradi."""
                return int((value or "0").replace(",", ""))

            markaz_fiks = to_int(row.get("Markaz Fiks"))
            markaz_kpi = to_int(row.get("Markaz KPI"))
            bonus = to_int(row.get("Markaz Bonus"))
            avans = to_int(row.get("Markaz Avans"))
            soliq = to_int(row.get("Markaz Soliq"))
            plastikka = to_int(row.get("Markaz Plastikka"))
            beriladi = to_int(row.get("Markaz Beriladi"))

            maktab_fiks = to_int(row.get("Maktab Fiks"))
            maktab_kpi = to_int(row.get("Maktab KPI"))
            maktab_avans = to_int(row.get("Maktab Avans"))
            maktab_soliq = to_int(row.get("Maktab Soliq"))
            maktab_plastikka = to_int(row.get("Maktab Plastikka"))
            maktab_beriladi = to_int(row.get("Maktab Beriladi"))
            hisoblangan = to_int(row.get("Hisoblangan"))

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
                f"💵 <b>Beriladigan:</b> {int(jami):,} so'm"
            ).replace(",", " ")

            await update.message.reply_text(text, parse_mode="HTML")
            return

    await update.message.reply_text("Siz ro'yxatdan o'tmagansiz yoki ma'lumot topilmadi.")

# ⚠ Xatolikka ariza komandasi
async def xatolikka_ariza_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clickup_link = "https://forms.clickup.com/9008240922/f/8cexp8u-25458/MNEA2WK9X4WIAAAR5J"
    await update.message.reply_text(
        f"📝 Xatolik yuzasidan ariza qoldirish uchun ushbu havolani bosing: \n\n"
        f"<a href='{clickup_link}'>👉 Ariza qoldirish</a>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# ⚠ Bolimlarga murojat komandasi
async def bolimlarga_murojat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clickup_link = "https://forms.clickup.com/9008240922/p/f/8cexp8u-2258/IT3FQOY51OU6GAL1OL/bolimlargamurojaatuchun"
    await update.message.reply_text(
        f"📄 Bo'limlarga murojat qoldirish uchun ushbu havolani bosing: \n\n"
        f"<a href='{clickup_link}'>👉 Bo'limlarga murojat</a>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    
# /cancel komandasi
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ro'yxatdan o'tish bekor qilindi.")
    return ConversationHandler.END

# Botni ishga tushirish
def main():
    app = ApplicationBuilder().token("7781412220:AAEiCJCmpNRoz6cP9CLoGoq3KqJi2aSNvD4").build()

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
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(⚠ Xatolikka ariza)$"), xatolikka_ariza_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^(📋 Bo'limlarga murojat)$"), bolimlarga_murojat_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
