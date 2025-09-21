"""Handler for editing an existing expense entry in the database."""
import logging
from telegram import Message, Update

from expanses_tracker.application.features.add_or_edit_expense.expense_notice import generate_notice
from expanses_tracker.application.models.expense import ExpenseSchema
from expanses_tracker.application.utils.message_parser import get_message_args
from expanses_tracker.persistence.database_context.database import DatabaseFactory
from expanses_tracker.persistence.repositories.repository import ExpenseRepository

log = logging.getLogger(__name__)

async def edit_handler(msg: Message, msg_id: int, update: Update):
    """Handle editing an existing expense entry in the database."""
    assert msg.edit_date is not None, "Message edit date can't be None for edited messages."
    try:
        arguments = get_message_args(msg.text, msg.edit_date)
    except ValueError as e:
        await msg.reply_text(str(e), reply_to_message_id=msg_id)
        await msg.reply_text("Entry not updated.", reply_to_message_id=msg_id)
        return
    # Get chat ID
    chat_id = update.effective_chat.id if update.effective_chat else 0
    user_id = update.effective_user.id if update.effective_user else 0
    # Update expense in database
    with DatabaseFactory.get_session() as session:
        try:
            expense = ExpenseRepository.update_expense(
                session=session,
                updated_expense=ExpenseSchema.model_construct(
                    msg_id=msg_id,
                    chat_id=chat_id,
                    user_id=user_id,
                    amount=arguments.amount,
                    description=arguments.description,
                    type=arguments.type,
                    category=arguments.category,
                    date=arguments.date
                )
            )
            if expense:
                await generate_notice(update, msg_id, msg, expense, msg)
            else:
                await msg.reply_text(
                    "No existing expense found to update.",
                    reply_to_message_id=msg.message_id
                )
        except Exception as e:
            log.error("Error updating expense: %s", e)
            await msg.reply_text(
                f"Error updating expense: {str(e)}",
                reply_to_message_id=msg.message_id
            )
