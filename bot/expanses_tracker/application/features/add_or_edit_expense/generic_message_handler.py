"""Generic message handler for adding or editing expenses."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from expanses_tracker.application.features.add_or_edit_expense.add_expense.add_handler import (
    add_handler
)
from expanses_tracker.application.features.add_or_edit_expense.edit_expense.edit_handler import (
    edit_handler
)
from expanses_tracker.application.utils.decorators import ensure_access_guard

log = logging.getLogger(__name__)

@ensure_access_guard
async def generic_message_handler(update: Update, _: ContextTypes.DEFAULT_TYPE):
    """Handle generic messages for adding or editing outcomes."""
    if (msg := update.effective_message) is None:
        log.warning("No effective message found in update.")
        return
    msg_id = msg.message_id
    if update.edited_message or update.edited_channel_post:
        await edit_handler(msg, msg_id, update)
    elif update.message or update.channel_post:
        await add_handler(msg, msg_id, update)
