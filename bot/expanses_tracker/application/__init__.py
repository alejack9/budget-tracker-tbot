"""Application registration for the Telegram bot."""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from expanses_tracker.application.features.add_or_edit_expense.generic_message_handler import (
    generic_message_handler,
)
from expanses_tracker.application.features.delete_expense.delete_command_handler import (
    delete_command_handler
)
from expanses_tracker.application.utils.decorators import ensure_access_guard
from expanses_tracker.application.features.buttons import setup_buttons_handlers
from expanses_tracker.application.features.get_expenses import get_command_handler

log = logging.getLogger(__name__)

@ensure_access_guard
async def __cmd_start__(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if message := update.effective_message:
        # TODO to update
        await message.reply_text(
            "Hi! I'm your Expense Tracker Bot.\n\n"
            "Send me expenses in this format:\n"
            "- <amount> <description> [category] [type] [date]\n\n"
            "Examples:\n"
            "10 groceries food need\n"
            "25.50 restaurant food want 15/09\n"
            "100/2 shared bill\n\n"
    )

def application_registration(app):
    """Register application handlers for the Telegram bot."""
    app.add_handler(CommandHandler("start", __cmd_start__))
    app.add_handler(CommandHandler("delete", delete_command_handler))
    app.add_handler(CommandHandler("get", get_command_handler))
    app.add_handler(MessageHandler(~filters.COMMAND, generic_message_handler), group=1)
    setup_buttons_handlers(app)
    return app
