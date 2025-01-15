from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    print(f"Your chat ID is: {chat_id}")
    await update.message.reply_text(f"Your chat ID is: {chat_id}")

if __name__ == '__main__':
    application = ApplicationBuilder().token("7878794010:AAE-E7zRnmO6xt06Gv8cuDLCkxOfUlmPZFQ").build()

    application.add_handler(CommandHandler("start", start))
    application.run_polling()
