"""Handles the /delete command to soft delete an outcome."""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes

from expanses_tracker.application.models.button_data_dto import BUTTON_ACTIONS, ButtonDataDto
from expanses_tracker.application.models.constants import UNDO_GRACE_SECONDS
from expanses_tracker.application.utils.decorators import ensure_access_guard
from expanses_tracker.persistence.database_context.database import DatabaseFactory
from expanses_tracker.persistence.repositories.repository import OutcomeRepository

log = logging.getLogger(__name__)

async def __delete_notice_job__(context: ContextTypes.DEFAULT_TYPE, notice: Message, chat_id: int, message_id: int, user_id: int):
    try:
        deleted = False
        with DatabaseFactory.get_session() as session:
            deleted = OutcomeRepository.delete_outcome(session, message_id, chat_id, user_id)
        if deleted:
            await context.bot.edit_message_text("Deleted.", chat_id=notice.chat_id, message_id=notice.message_id)
        else:
            log.debug("Outcome not found.")
    except Exception as e:
        # Fine if it's already gone or not deletable
        log.debug("Notice delete skipped: %s", e)

async def __countdown_callback__(ctx, notice, btn):
    job_data = ctx.job.data
    remaining = job_data['remaining']
    if remaining > 0:
        try:
            await ctx.bot.edit_message_text(
                f"Deleted. Tap to restore ({remaining}s).",
                chat_id=notice.chat_id,
                message_id=notice.message_id,
                reply_markup=InlineKeyboardMarkup([[btn]])
            )
        except Exception as e:
            log.debug("Countdown update skipped: %s", e)
        job_data['remaining'] -= 1
    else:
        ctx.job.schedule_removal()

async def __soft_delete_expense__(
        message_id: int,
        chat_id: int,
        user_id: int,
        message: Message,
        context: ContextTypes.DEFAULT_TYPE):
    # Delete outcome from database
    with DatabaseFactory.get_session() as session:
        try:
            success = OutcomeRepository.soft_delete(session, message_id, chat_id, user_id)
            if not success:
                await message.reply_text(
                    "Outcome record not found.",
                    reply_to_message_id=message_id)
                return
            # Post a short-lived Restore notice with an inline button
            btn = InlineKeyboardButton(
                text="↩️ Restore",
                callback_data=ButtonDataDto(
                    action=BUTTON_ACTIONS.RESTORE,
                    chat_id=chat_id,
                    message_id=message_id).model_dump_json(exclude_none=True,exclude_defaults=True,exclude_unset=True),
            )
            notice = await message.reply_text(
                f"Deleted. Tap to restore ({UNDO_GRACE_SECONDS}s).",
                reply_markup=InlineKeyboardMarkup([[btn]]),
                reply_to_message_id=message_id,
            )

            # Start the countdown job
            assert context.job_queue is not None
            context.job_queue.run_repeating(
                lambda ctx: __countdown_callback__(ctx, notice, btn),
                interval=1,
                first=1,
                name=f"countdown_notice_{notice.chat_id}_{notice.message_id}",
                data={'remaining': UNDO_GRACE_SECONDS - 1}
            )
            # Schedule the final deletion
            context.job_queue.run_once(
                lambda ctx: __delete_notice_job__(ctx, notice, chat_id, message_id, user_id),
                when=UNDO_GRACE_SECONDS,
                name=f"del_notice_{notice.chat_id}_{notice.message_id}",
            )
        except Exception as e:
            log.error("Error deleting outcome: %s", e)
            await message.reply_text(f"Error deleting outcome: {str(e)}", reply_to_message_id=message_id)

@ensure_access_guard
async def delete_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /delete command to soft delete an outcome."""
    if not update.message or not update.effective_chat or not update.effective_user:
        return
    # get message ID of the replied message
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to the message of the outcome you want to delete.", reply_to_message_id=update.message.message_id)
        return
    # get chat ID
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    # get message ID
    message_id = update.message.reply_to_message.message_id
    await __soft_delete_expense__(message_id, chat_id, user_id, update.message, context)
