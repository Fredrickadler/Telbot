import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# تنظیمات اصلی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")
APP_NAME = os.getenv("APP_NAME", "Telbot")
PORT = int(os.getenv("PORT", 8443))
WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.txt")

def load_words():
    """بارگیری کلمات از فایل با مدیریت خطا"""
    try:
        if os.path.exists(WORDS_FILE):
            with open(WORDS_FILE, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except:
        return []

def start(update: Update, context: CallbackContext):
    """ارسال کیبورد شیشه‌ای"""
    keyboard = [
        [InlineKeyboardButton("12 مورد", callback_data='12'),
         InlineKeyboardButton("24 مورد", callback_data='24')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '⚡ ربات انتخاب تصادفی ارزهای دیجیتال\n'
        'همیشه 1 ولت در نتایج وجود خواهد داشت!\n'
        'تعداد مورد نظر را انتخاب کنید:',
        reply_markup=reply_markup
    )

def button_handler(update: Update, context: CallbackContext):
    """پردازش کلیک دکمه‌ها"""
    query = update.callback_query
    query.answer()
    
    words = load_words()
    count = int(query.data)
    
    if len(words) + 1 < count:  # +1 برای ولت
        query.edit_message_text(f"⚠️ فقط {len(words)} مورد در لیست وجود دارد!")
        return
    
    # انتخاب تصادفی + اضافه کردن 1 ولت
    selected = random.sample(words, count-1) if words else []
    selected.append("1 ولت")  # اضافه کردن حتمی 1 ولت
    random.shuffle(selected)  # مخلوط کردن نتایج
    
    # نمایش نتایج
    result = "\n".join(f"• {item}" for item in selected)
    query.edit_message_text(
        f"✅ {count} مورد تصادفی:\n\n{result}\n\n"
        "⚡ همیشه 1 ولت در شبکه موجود است!"
    )

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    
    if 'render' in os.getenv("RENDER", "").lower():
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.onrender.com/{TOKEN}"
        )
        print(f"🤖 ربات آنلاین روی آدرس: https://{APP_NAME}.onrender.com")
    else:
        updater.start_polling()
        print("🤖 ربات در حالت توسعه (Polling) اجرا شد...")

    updater.idle()

if __name__ == '__main__':
    main()