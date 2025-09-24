"""Handler for the restore button in the expense tracker bot."""
import logging
from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes
from expanses_tracker.application.models.button_data_dto import ButtonActions, ButtonDataDto
from expanses_tracker.application.models.constants import UNDO_GRACE_SECONDS
from expanses_tracker.application.utils.decorators import button_callback
from expanses_tracker.persistence.database_context.database import DatabaseFactory
from expanses_tracker.persistence.repositories.repository import ExpenseRepository

log = logging.getLogger(__name__)

@button_callback(ButtonActions.RESTORE)
async def restore_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the restore button press."""
    chat_id = data.chat_id
    msg_id = data.message_id
    uid = update.effective_user.id if update.effective_user else 0

    if not query.message or not isinstance(query.message, Message):
        log.error("No message found in callback query: %s", query)
        return
    with DatabaseFactory.get_session() as session:
        try:
            restored = ExpenseRepository.restore(
                session,
                chat_id=chat_id,
                message_id=msg_id,
                user_id=uid,
                undo_grace_seconds=UNDO_GRACE_SECONDS)
            if restored:
                await query.message.reply_text("Restored", reply_to_message_id=msg_id)
                try:
                    if query.message:
                        await query.message.delete()
                except Exception:
                    pass
            else:
                await query.message.reply_text("Restore window expired or not allowed.", reply_to_message_id=msg_id)
        except Exception as e:
            log.exception("Restore failed")
            await query.message.reply_text(f"Error: {e}", reply_to_message_id=msg_id)
