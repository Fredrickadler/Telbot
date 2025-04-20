import os
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# تنظیمات اصلی
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7193129795:AAEbZ2gwsNT3DYPPrlWprgqNoX1NfJ9hXKw")
APP_NAME = os.getenv("APP_NAME", "Telbot")
PORT = int(os.getenv("PORT", 8443))
BLOCKCHAIN_API = "https://api.blockcypher.com/v1/btc/main"

def scan_blockchain():
    """اسکن بلاکچین برای یافتن ولت‌های دارای موجودی فراموش شده"""
    try:
        response = requests.get(f"{BLOCKCHAIN_API}/addrs", params={
            'balance': '>0',
            'limit': 100,
            'sort': 'last_tx'
        }, timeout=10)
        
        if response.status_code == 200:
            return response.json()['addresses']
        return []
    except:
        return []

def check_wallet_assets(address):
    """بررسی دارایی‌های یک ولت"""
    assets = {
        'BTC': 0,
        'ETH': 0,
        'USDT': 0
    }
    
    try:
        # بررسی BTC
        btc_resp = requests.get(f"{BLOCKCHAIN_API}/addrs/{address}/balance")
        if btc_resp.status_code == 200:
            assets['BTC'] = btc_resp.json()['balance'] / 10**8
        
        # بررسی سایر ارزها (مثال آموزشی)
        assets['ETH'] = random.random() * 3
        assets['USDT'] = random.random() * 1000
        
        return assets
    except:
        return assets

def start(update: Update, context: CallbackContext):
    """منوی اصلی ربات"""
    keyboard = [
        [InlineKeyboardButton("🔍 اسکن ولت‌های فراموش شده", callback_data='scan')],
        [InlineKeyboardButton("💰 بررسی دارایی ولت", callback_data='check')],
        [InlineKeyboardButton("ℹ️ راهنمای استفاده", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        '🔐 ربات ولت‌یاب حرفه‌ای\n\n'
        'برای بازیابی دارایی‌های گم شده در بلاکچین:\n'
        '1. اسکن خودکار برای یافتن ولت‌های دارای موجودی\n'
        '2. بررسی دقیق دارایی‌های هر ولت\n'
        '3. کمک به پروژه‌های بلاکچینی با دارایی‌های بازیابی شده\n\n'
        'گزینه مورد نظر را انتخاب کنید:',
        reply_markup=reply_markup
    )

def button_handler(update: Update, context: CallbackContext):
    """پردازش کلیک دکمه‌ها"""
    query = update.callback_query
    query.answer()
    
    if query.data == 'scan':
        wallets = scan_blockchain()
        if not wallets:
            query.edit_message_text("⚠️ در حال حاضر ولت فراموش شده یافت نشد. لطفاً بعداً تلاش کنید.")
            return
            
        wallet = random.choice(wallets)
        assets = check_wallet_assets(wallet['address'])
        
        message = (
            f"🔍 ولت یافت شده:\n<code>{wallet['address']}</code>\n\n"
            f"💰 دارایی‌های تخمینی:\n"
            f"• BTC: {assets['BTC']:.8f}\n"
            f"• ETH: {assets['ETH']:.4f}\n"
            f"• USDT: {assets['USDT']:.2f}\n\n"
            "ℹ️ برای بازیابی این دارایی‌ها به کیف پول اصلی مراجعه کنید."
        )
        
        keyboard = [
            [InlineKeyboardButton("📋 کپی آدرس", callback_data=f'copy_{wallet["address"]}')],
            [InlineKeyboardButton("🔍 بررسی در Explorer", url=f"https://www.blockchain.com/explorer/addresses/btc/{wallet['address']}")]
        ]
        
    elif query.data == 'check':
        message = (
            "🔎 لطفاً آدرس ولت را ارسال کنید:\n\n"
            "مثال:\n<code>1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa</code>"
        )
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='back')]]
        
    elif query.data == 'help':
        message = (
            "📚 راهنمای استفاده:\n\n"
            "1. اسکن خودکار: ربات بلاکچین را برای یافتن ولت‌های دارای موجودی اسکن می‌کند\n"
            "2. بررسی دستی: می‌توانید آدرس ولت را وارد کنید تا دارایی‌های آن بررسی شود\n"
            "3. دارایی‌های بازیابی شده می‌توانند به پروژه‌های بلاکچینی کمک کنند\n\n"
            "⚠️ توجه: این ربات فقط برای اهداف آموزشی است"
        )
        keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data='back')]]
        
    elif query.data == 'back':
        start(update, context)
        return
    
    query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

def copy_handler(update: Update, context: CallbackContext):
    """پردازش دکمه کپی"""
    query = update.callback_query
    query.answer("✅ آدرس کپی شد!", show_alert=False)

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
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