import logging
from telegram import CallbackQuery, Update
from bot.expanses_tracker.application.models.button_data_dto import ButtonDataDto
from bot.expanses_tracker.application.models.constants import UNDO_GRACE_SECONDS
from bot.expanses_tracker.application.utils.decorators import button_callback
from bot.expanses_tracker.persistence.database_context.database import DatabaseFactory
from bot.expanses_tracker.persistence.repositories.repository import ExpenseRepository

log = logging.getLogger(__name__)

@button_callback("restore")
async def restore_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update):
    try:
        chat_id = data.chat_id
        msg_id = data.message_id
        uid = update.effective_user.id if update.effective_user else 0
    except Exception:
        await query.answer("Invalid restore data.", show_alert=True)
        return
    session = DatabaseFactory.get_session()
    try:
        restored = ExpenseRepository.restore(session, chat_id=chat_id, message_id=msg_id, user_id=uid, undo_grace_seconds=UNDO_GRACE_SECONDS)
        if restored:
            await query.answer("Restored")
            try:
                if query.message:
                    await query.message.delete()
            except Exception:
                pass
        else:
            await query.answer("Restore window expired or not allowed.", show_alert=True)
    except Exception as e:
        log.exception("Restore failed")
        await query.answer(f"Error: {e}", show_alert=True)
    finally:
        session.close()
