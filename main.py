import os
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# تنظیمات اصلی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")  # توکن شما
APP_NAME = os.getenv("APP_NAME", "Telbot")  # نام پروژه در Render
PORT = int(os.getenv("PORT", 8443))  # پورت پیشفرض Render
WORDS_FILE = "words.txt"  # فایل ذخیره کلمات

# بررسی وجود توکن
if not TOKEN:
    raise ValueError("❌ توکن ربات یافت نشد! لطفاً TELEGRAM_BOT_TOKEN را تنظیم کنید.")

def load_words():
    """بارگیری کلمات از فایل با مدیریت خطاها"""
    try:
        # بررسی وجود فایل
        if not os.path.exists(WORDS_FILE):
            print(f"⚠️ فایل {WORDS_FILE} یافت نشد!")
            return []
            
        # خواندن فایل با کدگذاری UTF-8
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
            print(f"✅ تعداد کلمات خوانده شده: {len(words)}")  # لاگ برای دیباگ
            return words
            
    except Exception as e:
        print(f"❌ خطا در خواندن فایل: {e}")
        return []  # بازگرداندن لیست خالی اگر خطا رخ داد

def start(update: Update, context: CallbackContext):
    """دستور /start"""
    update.message.reply_text("🎲 سلام! لطفاً عدد 12 یا 24 را ارسال کنید:")

def handle_message(update: Update, context: CallbackContext):
    """پردازش پیام کاربر"""
    text = update.message.text
    words = load_words()  # بارگیری کلمات
    
    if not words:
        update.message.reply_text("⚠️ فایل کلمات خالی است یا خطایی رخ داده!")
        return
    
    if text == "12" or text == "24":
        count = int(text)
        if len(words) < count:
            update.message.reply_text(f"⚠️ فقط {len(words)} کلمه موجود است!")
        else:
            selected = random.sample(words, count)
            update.message.reply_text(f"✅ {count} کلمه تصادفی:\n\n" + "\n".join(selected))
    else:
        update.message.reply_text("❌ لطفاً فقط عدد 12 یا 24 ارسال کنید!")

def main():
    """تنظیمات اصلی ربات"""
    # چک کردن محیط اجرا (Render یا لوکال)
    is_render = 'render' in os.getenv("RENDER", "").lower()
    
    # مقداردهی ربات
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    # ثبت دستورات
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # حالت استقرار (Webhook در Render)
    if is_render:
        webhook_url = f"https://{APP_NAME}.onrender.com/{TOKEN}"
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=webhook_url
        )
        print(f"🤖 ربات با Webhook در Render اجرا شد:\n{webhook_url}")
    else:  # حالت توسعه (Polling)
        updater.start_polling()
        print("🤖 ربات در حالت توسعه (Polling) اجرا شد...")

    updater.idle()

if __name__ == '__main__':
    main()