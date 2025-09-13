import logging
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes

from expanses_tracker.application.features.delete_expense.delete_command_handler import __soft_delete_expense__
from expanses_tracker.application.models.button_data_dto import ButtonDataDto
from expanses_tracker.application.utils.decorators import button_callback

log = logging.getLogger(__name__)

@button_callback("delete")
async def delete_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await query.answer()
    chat_id = data.chat_id
    message_id = data.message_id
    uid = update.effective_user.id if update.effective_user else 0
    await __soft_delete_expense__(message_id, chat_id, uid, update, context)
