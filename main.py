import os
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")  # توکن را در محیط Render تنظیم کنید
PORT = int(os.getenv("PORT", 8443))  # برای Webhook
APP_NAME = os.getenv("APP_NAME")  # نام برنامه در Render

WORDS_FILE = "words.txt"

def load_words():
    if not os.path.exists(WORDS_FILE):
        return []
    with open(WORDS_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "سلام! من ربات انتخاب تصادفی کلمات هستم.\n"
        "لطفاً تعداد مورد نظر را انتخاب کنید (12 یا 24):"
    )

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    words = load_words()
    
    if not words:
        update.message.reply_text("⚠️ فایل کلمات خالی است!")
        return
    
    if text in ('12', '24'):
        count = int(text)
        if count > len(words):
            update.message.reply_text(f"⚠️ فقط {len(words)} کلمه موجود است!")
            return
            
        selected = random.sample(words, count)
        update.message.reply_text("🎲 کلمات تصادفی:\n\n" + "\n".join(selected))
    else:
        update.message.reply_text("❌ لطفاً فقط 12 یا 24 وارد کنید!")

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # اگر روی Render اجرا می‌شود، از Webhook استفاده کن
    if APP_NAME:  # یعنی روی Render است
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.onrender.com/{TOKEN}"
        )
    else:  # حالت لوکال (برای تست)
        updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
