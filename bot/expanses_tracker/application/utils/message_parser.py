"""Message parsing utilities for the application."""

import logging
from datetime import datetime
import re
import shlex
from typing import Optional

from expanses_tracker.application.models.constants import CATEGORIES, TYPES
from expanses_tracker.application.models.expense import ExpenseDto

log = logging.getLogger(__name__)

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

def __get_message_type__(parts: list[str]) -> tuple[Optional[str], list[str]]:
    return __get_message_domain__(parts, TYPES)

def __get_message_category__(parts: list[str]) -> tuple[Optional[str], list[str]]:
    return __get_message_domain__(parts, CATEGORIES)

# valid strings formats:
# - 10 spesa casa food need -> type: need, category: food, amount: 10, description: spesa casa
# - 10.5 spesa casa food need -> type: need, category: food, amount: 10.5, description: spesa casa
# - 10.50 spesa casa food need -> type: need, category: food, amount: 10.50, description: spesa casa
# - 10 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa
# - 10/2 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 5 (10/2), description: spesa
# - 10 spesa casa 21/05 -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa casa, date: 21/05/current_year
# - 10 spesa casa food need 21/05 -> type: need, category: food, amount: 10, description: spesa casa, date: 21/05/current_year
def get_message_args(text: str | None, date: datetime) -> ExpenseDto:
    """Parse a message text to extract expense details."""
    if text is None or not text.strip():
        raise ValueError("Empty command. Not enough parameters.")
    # Escape apostrophes embedded in words so shlex keeps the token intact
    # Example: "4 that's ok" becomes "4 that\'s ok"
    sanitized_text = re.sub(r"(?<=\w)'(?=\w)", r"\\'", text)
    try:
        parts = shlex.split(sanitized_text)
    except ValueError as exc:
        log.warning("Exception while splitting message text: %s", exc)
        raise ValueError("Ambiguous command. Not enough parameters.") from None
    if not parts:
        raise ValueError("Ambiguous command. Not enough parameters.")

    # Extract date
    out_date, parts = __get_message_date__(parts, date)

    # Extract type and category
    out_type, parts = __get_message_type__(parts)
    out_cat, parts = __get_message_category__(parts)

    if len(parts) < 2:
        raise ValueError("Ambiguous command. Not enough parameters.")

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
    return ExpenseDto(
        amount=out_amount,
        description=out_desc,
        type=out_type,
        category=out_cat,
        date=out_date
    )
