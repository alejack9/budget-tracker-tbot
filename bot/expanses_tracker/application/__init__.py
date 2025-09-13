
from pydantic_core import ValidationError
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import logging
from bot.expanses_tracker.application.features.add_or_edit_expense import generic_message_handler
from bot.expanses_tracker.application.features.delete_expense.delete_command_handler import delete_command_handler
from bot.expanses_tracker.application.models.button_data_dto import BTN_CALLBACKS, ButtonDataDto
from bot.expanses_tracker.application.utils.decorators import ensure_access_guard

__log__ = logging.getLogger(__name__)

@ensure_access_guard
async def __cmd_start__(update: Update, _: ContextTypes.DEFAULT_TYPE):
    # TODO to update
    await update.message.reply_text(
        "Hi! I'm your Expense Tracker Bot.\n\n"
        "Send me expenses in this format:\n"
        "- <amount> <description> [category] [type] [date]\n\n"
        "Examples:\n"
        "10 groceries food need\n"
        "25.50 restaurant food want 15/09\n"
        "100/2 shared bill\n\n"
    )

@ensure_access_guard
async def __button_cb__(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        data = ButtonDataDto.model_validate_json(query.data)
    except ValidationError:
        __log__.error("Invalid callback data: %s", query.data)
        return
    if data.action in BTN_CALLBACKS:
        handler = BTN_CALLBACKS[data.action]
        await handler(query, data, update)
    else:
        __log__.error("Unknown action in data: %s", data)
        await query.answer(f"Unknown action. Data: {data}", show_alert=True)

def application_registration(app):
    app.add_handler(CommandHandler("start", __cmd_start__))
    app.add_handler(CommandHandler("delete", delete_command_handler)) 
    app.add_handler(MessageHandler(~filters.COMMAND, generic_message_handler), group=1) 
    app.add_handler(CallbackQueryHandler(__button_cb__))
    return app
