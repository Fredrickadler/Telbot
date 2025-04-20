import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# تنظیمات اصلی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")
APP_NAME = os.getenv("APP_NAME", "Telbot")
PORT = int(os.getenv("PORT", 8443))
WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.txt")

# کلمات پیش‌فرض (اگر فایل خوانده نشد)
DEFAULT_WORDS = ["گل", "ماه", "کتاب", "123", "456", "ولت"]

def load_words():
    """بارگیری کلمات با مدیریت خطا"""
    try:
        if os.path.exists(WORDS_FILE):
            with open(WORDS_FILE, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f if line.strip()]
                if "ولت" not in words:  # اطمینان از وجود کلمه "ولت"
                    words.append("ولت")
                return words
        return DEFAULT_WORDS
    except:
        return DEFAULT_WORDS

def start(update: Update, context: CallbackContext):
    """ارسال کیبورد شیشه‌ای"""
    keyboard = [
        [InlineKeyboardButton("12 کلمه", callback_data='12')],
        [InlineKeyboardButton("24 کلمه", callback_data='24')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('🎲 تعداد کلمات مورد نظر را انتخاب کنید:', reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext):
    """پردازش کلیک دکمه‌ها"""
    query = update.callback_query
    query.answer()
    
    words = load_words()
    count = int(query.data)
    
    if len(words) < count:
        query.edit_message_text(f"⚠️ فقط {len(words)} کلمه موجود است!")
    else:
        # اطمینان از وجود "ولت" در نتایج
        selected = random.sample(words, count-1)
        selected.append("ولت")  # اضافه کردن حتمی کلمه "ولت"
        random.shuffle(selected)  # مخلوط کردن نتایج
        
        # نمایش کلمات با فاصله و پشت سر هم
        result = " ".join(selected)
        query.edit_message_text(f"✅ {count} کلمه تصادفی:\n\n{result}")

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
    else:
        updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()