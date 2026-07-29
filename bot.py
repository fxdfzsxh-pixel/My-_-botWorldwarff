from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8909171042:AAH8MUy9h_k_e2QNw4RXcOWWrp1jxMipj78"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات با موفقیت روی رندر راه‌اندازی شد!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("🚀 ربات تست روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
