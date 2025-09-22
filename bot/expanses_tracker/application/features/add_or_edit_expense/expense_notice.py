import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update

from expanses_tracker.application.models.button_data_dto import ButtonActions, ButtonDataDto
from expanses_tracker.application.models.outcome import OutcomeSchema

log = logging.getLogger(__name__)

async def generate_notice(update: Update, msg_id: int, msg: Message, outcome: OutcomeSchema, message_to_reply: Message) -> Message | None:
    # Get chat ID
    if not update.effective_chat:
        log.error("No effective chat found in update.")
        return
    chat_id = update.effective_chat.id
    del_btn = InlineKeyboardButton(
        text="🗑️ Delete",
        callback_data=ButtonDataDto(
            action=ButtonActions.DELETE,
            chat_id=chat_id,
            message_id=msg_id).model_dump_json(exclude_none=True,exclude_defaults=True,exclude_unset=True),
    )
    edit_category_btn = InlineKeyboardButton(
        text="🏷️ Edit Category",
        callback_data=ButtonDataDto(
            action=ButtonActions.CATEGORY,
            chat_id=chat_id,
            message_id=msg_id).model_dump_json(exclude_none=True,exclude_defaults=True,exclude_unset=True),
    )
    edit_type_btn = InlineKeyboardButton(
        text="🧩 Edit Type",
        callback_data=ButtonDataDto(
            action=ButtonActions.TYPE,
            chat_id=chat_id,
            message_id=msg_id).model_dump_json(exclude_none=True,exclude_defaults=True,exclude_unset=True),
    )
    notice = await message_to_reply.reply_text(
        f"Expense saved at {msg.date}:\n"
        f"Amount: {outcome.amount}\n"
        f"Description: {outcome.description}\n"
        f"Type: {outcome.type or 'Not specified'}\n"
        f"Category: {outcome.category or 'Not specified'}\n"
        f"Date: {outcome.date.strftime('%Y-%m-%d')}",
        reply_markup=InlineKeyboardMarkup([[del_btn, edit_category_btn, edit_type_btn]]),
        reply_to_message_id=msg.message_id
    )
    return notice
