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
    """ارسال کیبورد ساده"""
    keyboard = [
        [InlineKeyboardButton("12 کلمه", callback_data='12'),
         InlineKeyboardButton("24 کلمه", callback_data='24')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '🎲 ربات انتخاب تصادفی کلمات\n'
        'تعداد مورد نظر را انتخاب کنید:',
        reply_markup=reply_markup
    )

def button_handler(update: Update, context: CallbackContext):
    """پردازش کلیک دکمه‌ها"""
    query = update.callback_query
    query.answer()
    
    words = load_words()
    count = int(query.data)
    
    if len(words) < count:
        query.edit_message_text(f"⚠️ فقط {len(words)} کلمه در لیست وجود دارد!")
        return
    
    # انتخاب تصادفی
    selected = random.sample(words, count)
    
    # نمایش نتایج به صورت پیوسته و قابل کپی
    result = " ".join(selected)
    
    # ایجاد دکمه کپی
    copy_btn = InlineKeyboardButton("📋 کپی همه", callback_data='copy_' + result)
    keyboard = InlineKeyboardMarkup([[copy_btn]])
    
    query.edit_message_text(
        f"🔠 {count} کلمه تصادفی:\n\n{result}",
        reply_markup=keyboard
    )

def copy_handler(update: Update, context: CallbackContext):
    """پردازش دکمه کپی"""
    query = update.callback_query
    query.answer("✅ متن کپی شد!", show_alert=False)

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler, pattern='^(12|24)$'))
    dispatcher.add_handler(CallbackQueryHandler(copy_handler, pattern='^copy_'))
    
    if 'render' in os.getenv("RENDER", "").lower():
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.onrender.com/{TOKEN}"
        )
        print("🤖 ربات در حالت وب‌هوک اجرا شد")
    else:
        updater.start_polling()
        print("🤖 ربات در حالت توسعه اجرا شد")

    updater.idle()

if __name__ == '__main__':
    main()