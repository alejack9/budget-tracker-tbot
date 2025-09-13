import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.expanses_tracker.application.models.button_data_dto import ButtonDataDto
from bot.expanses_tracker.application.models.constants import UNDO_GRACE_SECONDS
from bot.expanses_tracker.application.utils.decorators import ensure_access_guard
from bot.expanses_tracker.persistence.database_context.database import DatabaseFactory
from bot.expanses_tracker.persistence.repositories.repository import ExpenseRepository

log = logging.getLogger(__name__)

async def __delete_notice_job__(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    message_id = job.data["message_id"]
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # Fine if it's already gone or not deletable
        log.debug("Notice delete skipped: %s", e)

async def __soft_delete_expense__(message_id: int, chat_id: int, user_id: int, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Delete expense from database
    session = DatabaseFactory.get_session()
    try:
        success = ExpenseRepository.soft_delete(session, message_id, chat_id, user_id)
        if not success:
            await update.message.reply_text(f"No expense found with ID={message_id}.")
        
        # Post a short-lived Restore notice with an inline button
        btn = InlineKeyboardButton(
            text="↩️ Restore",
            callback_data=ButtonDataDto(
                action="restore",
                chat_id=chat_id,
                message_id=message_id).model_dump_json(),
        )
        notice = await update.message.reply_text(
            f"Deleted. Tap to restore ({UNDO_GRACE_SECONDS}s).",
            reply_markup=InlineKeyboardMarkup([[btn]]),
            reply_to_message_id=message_id,
        )

        # Schedule deletion of the notice after UNDO_GRACE_SECONDS
        context.job_queue.run_once(
            __delete_notice_job__,
            when=UNDO_GRACE_SECONDS,
            data={"chat_id": notice.chat_id, "message_id": notice.message_id},
            name=f"del_notice_{notice.chat_id}_{notice.message_id}",
        )
    except Exception as e:
        log.error(f"Error deleting expense: {str(e)}")
        update.message.reply_text(f"Error deleting expense: {str(e)}")
    finally:
        session.close()

@ensure_access_guard
async def delete_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get message ID of the replied message
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to the message of the expense you want to delete.")
        return
    # get chat ID
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else 0
    # get message ID
    message_id = update.message.reply_to_message.message_id
    await __soft_delete_expense__(message_id, chat_id, user_id, update, context)
