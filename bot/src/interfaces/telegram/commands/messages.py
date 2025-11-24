from dataclasses import dataclass
from datetime import datetime
import re
import shlex
from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes
import logging
from dependency_injector.wiring import Provide, inject

from src.application.dto.add_expense import AddExpenseInput, AddExpenseOutput
from src.application.use_cases.add_expense import AddExpenseUseCase
from src.config.settings import Settings
from src.domain.entities.expense import Expense
from src.config.container import Container
from .access_guard import ensure_access_guard

log = logging.getLogger(__name__)

@dataclass
class MsgArgs:
    amount: float
    description: str
    type: Optional[str]
    category: Optional[str]
    date: datetime

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

# valid strings formats:
# - 10 spesa casa food need -> type: need, category: food, amount: 10, description: spesa casa
# - 10.5 spesa casa food need -> type: need, category: food, amount: 10.5, description: spesa casa
# - 10.50 spesa casa food need -> type: need, category: food, amount: 10.50, description: spesa casa
# - 10 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa
# - 10/2 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 5 (10/2), description: spesa
# - 10 spesa casa 21/05 -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa casa, date: 21/05/current_year
# - 10 spesa casa food need 21/05 -> type: need, category: food, amount: 10, description: spesa casa, date: 21/05/current_year
# guard already checked by generic_message_handler
@inject
async def add_handler(
    msg: Message,
    msg_id: int,
    update: Update,
    add_expense_use_case: AddExpenseUseCase = Provide[Container.add_expense_use_case],
    settings: Settings = Provide[Container.settings],
):
    """Handle adding a new outcome based on user message input."""
    try:
        arguments = _get_message_args(msg.text, msg.date, settings)
    except ValueError as e:
        await msg.reply_text(str(e), reply_to_message_id=msg.message_id)
        return

    # Get chat ID
    if not update.effective_chat:
        log.error("No effective chat found in update.")
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else 0

    try:
        add_expense_output = add_expense_use_case.execute(
            input_dto=AddExpenseInput(
                amount=arguments.amount,
                description=arguments.description,
                date=arguments.date,
                type=arguments.type,
                category=arguments.category,
                msg_id=msg_id,
                chat_id=chat_id,
                user_id=user_id,
                created_at=msg.date,
                updated_at=msg.date)
        )
        if not update.message:
            log.error("No message found in update.")
            return
        await _generate_notice(update, msg_id, msg, add_expense_output, update.message)
    except Exception as e:
        log.error("Error saving expense: %s", e)
        await msg.reply_text(
                f"Error saving expense: {str(e)}",
                reply_to_message_id=msg.message_id
            )

async def edit_handler(msg: Message, msg_id: int, update: Update):
    """Handle editing an existing outcome entry in the database."""
    pass
    # assert msg.edit_date is not None, "Message edit date can't be None for edited messages."
    # try:
    #     arguments = get_message_args(msg.text, msg.edit_date)
    # except ValueError as e:
    #     await msg.reply_text(str(e), reply_to_message_id=msg_id)
    #     await msg.reply_text("Entry not updated.", reply_to_message_id=msg_id)
    #     return
    # # Get chat ID
    # chat_id = update.effective_chat.id if update.effective_chat else 0
    # user_id = update.effective_user.id if update.effective_user else 0
    # # Update outcome in database
    # with DatabaseFactory.get_session() as session:
    #     try:
    #         outcome = OutcomeRepository.update_outcome(
    #             session=session,
    #             updated_outcome=OutcomeSchema.model_construct(
    #                 msg_id=msg_id,
    #                 chat_id=chat_id,
    #                 user_id=user_id,
    #                 amount=arguments.amount,
    #                 description=arguments.description,
    #                 type=arguments.type,
    #                 category=arguments.category,
    #                 date=arguments.date
    #             )
    #         )
    #         if outcome:
    #             await generate_notice(update, msg_id, msg, outcome, msg)
    #         else:
    #             await msg.reply_text(
    #                 "No existing expense found to update.",
    #                 reply_to_message_id=msg.message_id
    #             )
    #     except Exception as e:
    #         log.error("Error updating expense: %s", e)
    #         await msg.reply_text(
    #             f"Error updating expense: {str(e)}",
    #             reply_to_message_id=msg.message_id
    #         )

AMBIGUOUS_CMD_NOT_ENOUGH_PARAMS = "Ambiguous command. Not enough parameters."

def __get_message_date__(parts: list[str], default_date: datetime) -> tuple[datetime, list[str]]:
    """Extract date from the last element of parts if it matches d/m or d/m/yyyy format."""
    msg_dt = default_date
    date_token = parts[-1]
    # match d/m or d/m/yyyy
    date_match_candidate = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", date_token)
    to_return = default_date
    if date_match_candidate:
        day = int(date_match_candidate.group(1))
        month = int(date_match_candidate.group(2))
        year = int(date_match_candidate.group(3)) if date_match_candidate.group(3) else msg_dt.year
        try:
            to_return = datetime(year, month, day)
            parts.pop() # remove the date part
        except ValueError as e:
            log.warning("Exception while parsing date from message: %s", e)
            # Intentionally hide original cause from end users
            raise ValueError("Ambiguous command. Invalid date.") from None
    return to_return, parts

def __get_message_domain__(parts: list[str], domain: list[str]) -> tuple[Optional[str], list[str]]:
    """Extract type from the last element of parts if it matches a known type."""
    to_return = None
    if parts and parts[-1].lower() in domain:
        to_return = parts[-1].lower()
        parts.pop() # remove the type part
    return to_return, parts

def __get_message_type__(parts: list[str], settings: Settings) -> tuple[Optional[str], list[str]]:
    return __get_message_domain__(parts, settings.types)

def __get_message_category__(parts: list[str], settings: Settings) -> tuple[Optional[str], list[str]]:
    return __get_message_domain__(parts, settings.categories)

# valid strings formats:
# - 10 spesa casa food need -> type: need, category: food, amount: 10, description: spesa casa
# - 10.5 spesa casa food need -> type: need, category: food, amount: 10.5, description: spesa casa
# - 10.50 spesa casa food need -> type: need, category: food, amount: 10.50, description: spesa casa
# - 10 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa
# - 10/2 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 5 (10/2), description: spesa
# - 10 spesa casa 21/05 -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa casa, date: 21/05/current_year
# - 10 spesa casa food need 21/05 -> type: need, category: food, amount: 10, description: spesa casa, date: 21/05/current_year
def _get_message_args(text: str | None, date: datetime, settings: Settings) -> MsgArgs:
    """Parse a message text to extract outcome details."""
    if text is None or not text.strip():
        raise ValueError("Empty command. Not enough parameters.")
    # Escape apostrophes embedded in words so shlex keeps the token intact
    # Example: "4 that's ok" becomes "4 that\'s ok"
    sanitized_text = re.sub(r"(?<=\w)'(?=\w)", r"\\'", text)
    try:
        parts = shlex.split(sanitized_text)
    except ValueError as exc:
        log.warning("Exception while splitting message text: %s", exc)
        raise ValueError(AMBIGUOUS_CMD_NOT_ENOUGH_PARAMS) from None
    if not parts:
        raise ValueError(AMBIGUOUS_CMD_NOT_ENOUGH_PARAMS)

    # Extract date
    out_date, parts = __get_message_date__(parts, date)

    # Extract type and category
    out_type, parts = __get_message_type__(parts, settings)
    out_cat, parts = __get_message_category__(parts, settings)

    if len(parts) < 2:
        raise ValueError(AMBIGUOUS_CMD_NOT_ENOUGH_PARAMS)

    # Extract description
    out_desc = " ".join(parts[1:])

    # Extract amount
    amount_str = parts[0]
    try:
        if "/" in amount_str:
            nums = amount_str.split("/")
            if len(nums) != 2:
                raise ValueError("Ambiguous command. Invalid amount.")
            num1 = float(nums[0])
            num2 = float(nums[1])
            if num2 == 0:
                raise ZeroDivisionError("Ambiguous command. Division by zero in amount.")
            out_amount = round(num1 / num2, 2)
        else:
            out_amount = float(amount_str)
    except ZeroDivisionError as e:
        log.warning("Exception while parsing amount from message: %s", e)
        # Preserve user-friendly message while suppressing original context
        raise ValueError(str(e)) from e
    except ValueError as e:
        log.warning("Exception while parsing amount from message: %s", e)
        # Suppress original parsing error details to keep message concise
        raise ValueError("Ambiguous command. Invalid amount.") from None

    # Create and return the MessageArgs model instance
    return MsgArgs(
        amount=out_amount,
        description=out_desc,
        type=out_type,
        category=out_cat,
        date=out_date
    )


async def _generate_notice(update: Update, msg_id: int, msg: Message, add_expense_output: AddExpenseOutput, message_to_reply: Message) -> Message | None:
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
        f"Amount: {add_expense_output.expense.amount}\n"
        f"Description: {add_expense_output.expense.description}\n"
        f"Type: {add_expense_output.expense.type or 'Not specified'}\n"
        f"Category: {add_expense_output.expense.category or 'Not specified'}\n"
        f"Date: {add_expense_output.expense.date.strftime('%Y-%m-%d')}",
        reply_markup=InlineKeyboardMarkup([[del_btn, edit_category_btn, edit_type_btn]]),
        reply_to_message_id=msg.message_id
    )
    return notice
