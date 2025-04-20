import os
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# تنظیمات ضروری
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")  # توکن شما
APP_NAME = os.getenv("APP_NAME", "Telbot")  # نام پروژه در Render
PORT = int(os.getenv("PORT", 8443))  # پورت پیشفرض Render
WORDS_FILE = "words.txt"  # فایل ذخیره کلمات

# بررسی وجود توکن
if not TOKEN:
    raise ValueError("❌ توکن ربات یافت نشد! لطفاً TELEGRAM_BOT_TOKEN را تنظیم کنید.")

def load_words():
    """بارگیری کلمات از فایل"""
    try:
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ["گل", "ماه", "کتاب", "123", "456"]  # مقادیر پیشفرض اگر فایل وجود نداشت

def start(update: Update, context: CallbackContext):
    """دستور /start"""
    update.message.reply_text("🎲 سلام! لطفاً عدد 12 یا 24 را ارسال کنید:")

def handle_message(update: Update, context: CallbackContext):
    """پردازش پیام کاربر"""
    text = update.message.text
    words = load_words()
    
    if text == "12" or text == "24":
        count = int(text)
        if len(words) < count:
            update.message.reply_text(f"⚠️ فقط {len(words)} کلمه موجود است!")
        else:
            selected = random.sample(words, count)
            update.message.reply_text("✅ کلمات تصادفی:\n\n" + "\n".join(selected))
    else:
        update.message.reply_text("❌ لطفاً فقط عدد 12 یا 24 ارسال کنید!")

def main():
    """تنظیمات ربات"""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # دستورات
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # حالت استقرار روی Render
    if 'render' in os.getenv("RENDER", "").lower():  # تشخیص خودکار Render
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.onrender.com/{TOKEN}"
        )
        print(f"🤖 ربات آنلاین روی آدرس: https://{APP_NAME}.onrender.com")
    else:  # حالت توسعه (لوکال)
        updater.start_polling()
        print("🤖 ربات در حالت توسعه (Polling) اجرا شد...")

    updater.idle()

if __name__ == '__main__':
    main()