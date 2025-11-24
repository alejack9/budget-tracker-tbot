from telegram import Update
from telegram.ext import ContextTypes
from .access_guard import ensure_access_guard

@ensure_access_guard
async def start_handler(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if message := update.effective_message:
        # TODO to update
        await message.reply_text(
            "Hi! I'm your Expense Tracker Bot.\n\n"
            "Send me expenses in this format:\n"
            "- <amount> <description> [category] [type] [date]\n\n"
            "Examples:\n"
            "10 groceries food need\n"
            "25.50 restaurant food want 15/09\n"
            "100/2 shared bill"
    )
