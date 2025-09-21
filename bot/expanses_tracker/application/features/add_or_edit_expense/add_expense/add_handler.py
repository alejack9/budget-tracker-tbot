""" Handler for adding a new expense based on user message input. """
import logging
from telegram import Message, Update
from expanses_tracker.application.features.add_or_edit_expense.expense_notice import generate_notice
from expanses_tracker.application.utils.message_parser import get_message_args
from expanses_tracker.persistence.database_context.database import DatabaseFactory
from expanses_tracker.persistence.repositories.repository import OutcomeRepository

log = logging.getLogger(__name__)

# valid strings formats:
# - 10 spesa casa food need -> type: need, category: food, amount: 10, description: spesa casa
# - 10.5 spesa casa food need -> type: need, category: food, amount: 10.5, description: spesa casa
# - 10.50 spesa casa food need -> type: need, category: food, amount: 10.50, description: spesa casa
# - 10 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa
# - 10/2 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 5 (10/2), description: spesa
# - 10 spesa casa 21/05 -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa casa, date: 21/05/current_year
# - 10 spesa casa food need 21/05 -> type: need, category: food, amount: 10, description: spesa casa, date: 21/05/current_year
# guard already checked by generic_message_handler
async def add_handler(msg: Message, msg_id: int, update: Update):
    """Handle adding a new outcome based on user message input."""
    try:
        arguments = get_message_args(msg.text, msg.date)
    except ValueError as e:
        await msg.reply_text(str(e), reply_to_message_id=msg.message_id)
        return

    # Get chat ID
    if not update.effective_chat:
        log.error("No effective chat found in update.")
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else 0

    # Save outcome to database
    with DatabaseFactory.get_session() as session:
        try:
            outcome = OutcomeRepository.create_outcome(
                session=session,
                outcome=arguments,
                message_id=msg_id,
                chat_id=chat_id,
                user_id=user_id
            )
            if not update.message:
                log.error("No message found in update.")
                return
            await generate_notice(update, msg_id, msg, outcome, update.message)
        except Exception as e:
            log.error("Error saving expense: %s", e)
            await msg.reply_text(
                    f"Error saving expense: {str(e)}",
                    reply_to_message_id=msg.message_id
                )
