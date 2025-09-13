import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from bot.expanses_tracker.application.models.button_data_dto import ButtonDataDto
from bot.expanses_tracker.application.utils.message_parser import get_message_args
from bot.expanses_tracker.persistence.database_context.database import DatabaseFactory
from bot.expanses_tracker.persistence.repositories.repository import ExpenseRepository

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
    try:
        arguments = get_message_args(msg.text, msg.date)
    except ValueError as e:
        await msg.reply_text(str(e), reply_to_message_id=msg.message_id)
        return
        
    # Get chat ID
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else 0
    
    # Save expense to database
    session = DatabaseFactory.get_session()
    try:
        expense = ExpenseRepository.create_expense(
            session=session,
            expense=arguments,
            message_id=msg_id,
            chat_id=chat_id,
            user_id=user_id
        )
        del_btn = InlineKeyboardButton(
            text="🗑️ Delete",
            callback_data=ButtonDataDto(
                action="delete",
                chat_id=chat_id,
                message_id=msg_id).model_dump_json(),
        )
        notice = await update.message.reply_text(
            f"Expense saved with ID={msg_id} at {msg.date}:\n"
            f"Amount: {expense.amount}\n"
            f"Description: {expense.description}\n"
            f"Type: {expense.type or 'Not specified'}\n"
            f"Category: {expense.category or 'Not specified'}\n"
            f"Date: {expense.date.strftime('%Y-%m-%d')}",
            reply_markup=InlineKeyboardMarkup([[del_btn]]),
            reply_to_message_id=msg.message_id
        )
    except Exception as e:
        log.error(f"Error saving expense: {str(e)}")
        await msg.reply_text(
                f"Error saving expense: {str(e)}",
                reply_to_message_id=msg.message_id
            )
    finally:
        session.close()
