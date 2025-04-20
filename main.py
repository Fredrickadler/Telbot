import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# تنظیمات اصلی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")
APP_NAME = os.getenv("APP_NAME", "Telbot")
PORT = int(os.getenv("PORT", 8443))
WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.txt")

# کش برای کلمات
WORDS_CACHE = []

def load_words():
    """بارگیری کلمات از فایل با کش"""
    global WORDS_CACHE
    if not WORDS_CACHE:
        try:
            with open(WORDS_FILE, 'r', encoding='utf-8') as f:
                WORDS_CACHE = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"خطا در خواندن فایل: {e}")
            WORDS_CACHE = []
    return WORDS_CACHE

def generate_seed_phrase(word_count):
    """تولید عبارت بازیابی با بررسی تعداد کلمات"""
    words = load_words()
    if len(words) < word_count:
        return None
    return random.sample(words, word_count)

def start(update: Update, context: CallbackContext):
    """منوی اصلی با دکمه‌های فوری"""
    keyboard = [
        [InlineKeyboardButton("🔓 12 کلمه", callback_data='12'),
         InlineKeyboardButton("🔏 24 کلمه", callback_data='24')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '🔐 **ربات تولید عبارت بازیابی**\n\n'
        'تعداد مورد نظر را انتخاب کنید:',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

def button_handler(update: Update, context: CallbackContext):
    """پردازش سریع درخواست"""
    query = update.callback_query
    query.answer()
    
    word_count = int(query.data)
    seed_words = generate_seed_phrase(word_count)
    
    if not seed_words:
        query.edit_message_text(
            f"⚠️ فایل words.txt باید حداقل شامل {word_count} کلمه باشد!\n"
            f"تعداد کلمات موجود: {len(load_words())}"
        )
        return
    
    # نمایش سریع با قابلیت کپی
    formatted_words = "\n".join([f"{i+1}. {word}" for i, word in enumerate(seed_words)])
    copy_btn = InlineKeyboardButton("📋 کپی همه", callback_data='copy_' + " ".join(seed_words))
    
    query.edit_message_text(
        f"🔑 عبارت {word_count} کلمه‌ای:\n\n{formatted_words}",
        reply_markup=InlineKeyboardMarkup([[copy_btn]])
    )

def copy_handler(update: Update, context: CallbackContext):
    """تأیید کپی"""
    query = update.callback_query
    query.answer("✅ عبارت کپی شد!", show_alert=True)

def main():
    """تنظیمات بهینه شده ربات"""
    # پیش‌بارگیری کلمات
    load_words()
    
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler, pattern='^(12|24)$'))
    dispatcher.add_handler(CallbackQueryHandler(copy_handler, pattern='^copy_'))
    
    # حالت استقرار
    if os.getenv('RENDER'):
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.onrender.com/{TOKEN}",
            drop_pending_updates=True
        )
    else:
        updater.start_polling(drop_pending_updates=True)
    
    print(f"🤖 ربات آماده! تعداد کلمات بارگیری شده: {len(WORDS_CACHE)}")
    updater.idle()

if __name__ == '__main__':
    main()