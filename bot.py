import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

BOT_TOKEN = "8620659225:AAESvDGdlCc5A37ptL9evfugx4ncVSWZKGE"
CHANNEL_USERNAME = "abhigyan_codes"
API_URL = "http://dark-osint-number-api.vercel.app/?num="

def clean(text):
    if not text:
        return "N/A"
    return str(text).replace("_", " ").replace("*", "").replace("`", "").replace("[", "").replace("]", "")

async def check_membership(user_id, context):
    try:
        member = await context.bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_membership(user_id, context)
    if is_member:
        await update.message.reply_text(
            "✅ Access Granted!\n\n"
            "Send any mobile number to get info.\n"
            "Example: 9876543212"
        )
    else:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
        await update.message.reply_text(
            "❌ Access Denied!\n\nPlease join our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_membership(user_id, context)

    if not is_member:
        keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")]]
        await update.message.reply_text(
            "❌ Please join our channel first.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    number = update.message.text.strip()
    if not number.isdigit() or len(number) < 7:
        await update.message.reply_text("⚠️ Please send a valid phone number.")
        return

    await update.message.reply_text("🔍 Searching... Please wait.")

    try:
        response = requests.get(API_URL + number, timeout=15)
        data = response.json()

        if not data or data.get("error"):
            await update.message.reply_text("❌ No info found for this number.")
            return

        info = "📱 Number Info\n━━━━━━━━━━━━━━━━\n"
        info += f"🔢 Number: {number}\n\n"
        for key, value in data.items():
            if value and key != "error":
                info += f"• {key.replace('_', ' ').title()}: {clean(value)}\n"
        info += "\n━━━━━━━━━━━━━━━━\n🤖 @abhigyan_codes"

        await update.message.reply_text(info)

    except requests.exceptions.Timeout:
        await update.message.reply_text("⏳ Timeout. Try again.")
    except Exception:
        await update.message.reply_text("❌ Something went wrong. Try again later.")

def main():
    keep_alive()  # Flask server start — Render web service alive rahegi
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"Crashed: {e} — Restarting in 5s...")
            time.sleep(5)
