"""Handler for the /get command returning recent expenses."""
from __future__ import annotations

import logging
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from expanses_tracker.application.utils.decorators import ensure_access_guard
from expanses_tracker.application.utils.expense_formatter import format_recent_expenses
from expanses_tracker.persistence.database_context.database import DatabaseFactory
from expanses_tracker.persistence.repositories.repository import ExpenseRepository

log = logging.getLogger(__name__)

DEFAULT_LIMIT = 5
MAX_LIMIT = 50


def _parse_limit(args: Optional[list[str]]) -> Optional[int]:
    """Return a validated positive integer limit or None when parsing fails."""
    if not args:
        return DEFAULT_LIMIT
    candidate = args[0]
    try:
        parsed = int(candidate)
    except ValueError:
        return None
    if parsed <= 0:
        return None
    return min(parsed, MAX_LIMIT)


@ensure_access_guard
async def get_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply with the most recent expenses for the current chat/user."""
    message = update.message
    if not message or not update.effective_chat or not update.effective_user:
        return

    limit = _parse_limit(getattr(context, "args", None))
    if limit is None:
        await message.reply_text(
            "Please provide a positive number, e.g. /get 5.",
            reply_to_message_id=message.message_id,
        )
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    with DatabaseFactory.get_session() as session:
        try:
            expenses = ExpenseRepository.get_last_expenses(
                session=session,
                chat_id=chat_id,
                user_id=user_id,
                limit=limit,
            )
        except Exception as exc:
            log.error("Failed to fetch expenses: %s", exc)
            await message.reply_text(
                "Could not load expenses, please try again later.",
                reply_to_message_id=message.message_id,
            )
            return

    await message.reply_text(
        format_recent_expenses(expenses),
        reply_to_message_id=message.message_id,
        parse_mode=ParseMode.HTML,
    )
