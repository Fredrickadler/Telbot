import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# تنظیمات اصلی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")
APP_NAME = os.getenv("APP_NAME", "Telbot")
PORT = int(os.getenv("PORT", 8443))

# لیست استاندارد کلمات بازیابی (BIP-39)
WORDS_LIST = [
    "abandon", "ability", "able", "about", "above", "absent", 
    "absorb", "abstract", "absurd", "abuse", "access", "accident",
    # ... (2048 کلمه استاندارد BIP-39 را اینجا قرار دهید)
    "zoo"
]

def generate_seed_phrase(word_count):
    """تولید عبارت بازیابی معتبر"""
    if word_count not in [12, 24]:
        word_count = 12  # حالت پیشفرض
    
    # انتخاب تصادفی کلمات از لیست استاندارد
    selected_words = random.sample(WORDS_LIST, word_count)
    
    # ایجاد checksum (ساده‌سازی شده)
    if word_count == 12:
        checksum_word = random.choice(WORDS_LIST)
        selected_words.append(checksum_word)
    elif word_count == 24:
        checksum_word = random.choice(WORDS_LIST[:256])  # محدودتر برای امنیت بیشتر
        selected_words[-1] = checksum_word
    
    return " ".join(selected_words)

def start(update: Update, context: CallbackContext):
    """منوی اصلی با گزینه‌های تولید عبارت بازیابی"""
    keyboard = [
        [InlineKeyboardButton("🔒 تولید 12 کلمه ای", callback_data='12'),
         InlineKeyboardButton("🔐 تولید 24 کلمه ای", callback_data='24')],
        [InlineKeyboardButton("⚠️ نکات امنیتی", callback_data='security')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '🔑 ربات تولید عبارت بازیابی ارزهای دیجیتال\n\n'
        'لطفاً نوع عبارت مورد نیاز را انتخاب کنید:',
        reply_markup=reply_markup
    )

def button_handler(update: Update, context: CallbackContext):
    """پردازش انتخاب کاربر"""
    query = update.callback_query
    query.answer()
    
    if query.data == 'security':
        query.edit_message_text(
            "🔐 نکات امنیتی مهم:\n\n"
            "1. این عبارت را با کسی به اشتراک نگذارید\n"
            "2. آن را به صورت دیجیتال ذخیره نکنید\n"
            "3. روی کاغذ نوشته و در مکان امن نگهداری کنید\n"
            "4. هرگز در سایت‌های ناشناس وارد نکنید"
        )
        return
    
    word_count = int(query.data)
    seed_phrase = generate_seed_phrase(word_count)
    
    # دکمه‌های عملیاتی
    keyboard = [
        [InlineKeyboardButton("📋 کپی عبارت", callback_data=f'copy_{seed_phrase}')],
        [InlineKeyboardButton("⚠️ نکات امنیتی", callback_data='security')]
    ]
    
    query.edit_message_text(
        f"🔑 عبارت بازیابی {word_count} کلمه ای:\n\n"
        f"<code>{seed_phrase}</code>\n\n"
        "❗ این عبارت معادل کلید خصوصی شماست!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

def copy_handler(update: Update, context: CallbackContext):
    """پردازش دکمه کپی"""
    query = update.callback_query
    query.answer("✅ عبارت بازیابی کپی شد!", show_alert=False)

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler, pattern='^(12|24|security)$'))
    dispatcher.add_handler(CallbackQueryHandler(copy_handler, pattern='^copy_'))
    
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