
from telegram import Update
from telegram.ext import ContextTypes
import logging

from bot.expanses_tracker.application.features.add_or_edit_expense.add_expense.add_handler import add_handler
from bot.expanses_tracker.application.features.add_or_edit_expense.edit_expense.edit_handler import edit_handler
from bot.expanses_tracker.application.utils.decorators import ensure_access_guard

log = logging.getLogger(__name__)

@ensure_access_guard
async def generic_message_handler(update: Update, _: ContextTypes.DEFAULT_TYPE):
    msg_id = update.effective_message.message_id
    msg = update.effective_message  # message/channel_post/edited_* whichever exists

    if update.edited_message or update.edited_channel_post:
        await edit_handler(msg, msg_id, update)
    elif update.message or update.channel_post:
        await add_handler(msg, msg_id, update)
