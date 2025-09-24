"""Handler for the delete button in the expense tracker bot."""
import logging
from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes

from expanses_tracker.application.features.delete_expense.delete_command_handler import (
    __soft_delete_expense__
)
from expanses_tracker.application.models.button_data_dto import ButtonActions, ButtonDataDto
from expanses_tracker.application.utils.decorators import button_callback

log = logging.getLogger(__name__)

@button_callback(ButtonActions.DELETE)
async def delete_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the delete button press."""
    chat_id = data.chat_id
    message_id = data.message_id
    uid = update.effective_user.id if update.effective_user else 0
    if query.message and isinstance(query.message, Message):
        await __soft_delete_expense__(message_id, chat_id, uid, query.message, context)
    else:
        log.error("No message found in callback query: %s", query)
