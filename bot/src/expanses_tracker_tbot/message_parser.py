from datetime import datetime
import re
import shlex
from typing import Optional

from expanses_tracker_tbot.domain.constants import CATEGORIES, TYPES

def get_message_date(parts: list[str], default_date: datetime) -> tuple[datetime, list[str]]:
    """Extract date from the last element of parts if it matches d/m or d/m/yyyy format."""
    msg_dt = default_date
    date_token = parts[-1]
    date_match_candidate = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", date_token) # match d/m or d/m/yyyy
    to_return = default_date
    if date_match_candidate:
        day = int(date_match_candidate.group(1))
        month = int(date_match_candidate.group(2))
        year = int(date_match_candidate.group(3)) if date_match_candidate.group(3) else msg_dt.year
        try:
            to_return = datetime(year, month, day)
            parts.pop() # remove the date part
        except ValueError:
            raise ValueError("Ambiguous command. Invalid date.")
    return [to_return, parts]

def get_message_domain(parts: list[str], domain: list[str]) -> tuple[Optional[str], list[str]]:
    """Extract type from the last element of parts if it matches a known type."""
    to_return = None
    if parts and parts[-1].lower() in domain:
        to_return = parts[-1].lower()
        parts.pop() # remove the type part
    return [to_return, parts]

def get_message_type(parts: list[str]) -> tuple[Optional[str], list[str]]:
    return get_message_domain(parts, TYPES)

def get_message_category(parts: list[str]) -> tuple[Optional[str], list[str]]:
    return get_message_domain(parts, CATEGORIES)

# valid strings formats:
# - 10 spesa casa food need -> type: need, category: food, amount: 10, description: spesa casa
# - 10.5 spesa casa food need -> type: need, category: food, amount: 10.5, description: spesa casa
# - 10.50 spesa casa food need -> type: need, category: food, amount: 10.50, description: spesa casa
# - 10 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa
# - 10/2 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 5 (10/2), description: spesa
# - 10 spesa casa 21/05 -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa casa, date: 21/05/current_year
# - 10 spesa casa food need 21/05 -> type: need, category: food, amount: 10, description: spesa casa, date: 21/05/current_year
# TODO use pydantic model instead of dict
def get_message_args(text: str, date: datetime) -> dict:
    parts = shlex.split(text)
    if not parts:
        raise ValueError("Ambiguous command. Not enough parameters.")
    out = {}
    out_date, parts = get_message_date(parts, date)
    out["date"] = out_date
    out_type, parts = get_message_type(parts)
    out["type"] = out_type
    out_cat, parts = get_message_category(parts)
    out["category"] = out_cat
    if len(parts) < 2:
        raise ValueError("Ambiguous command. Not enough parameters.")
    out_desc = " ".join(parts[1:])
    out["description"] = out_desc
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
            out_amount = num1 / num2
        else:
            out_amount = float(amount_str)
        out["amount"] = out_amount
    except ZeroDivisionError as e:
        raise ValueError(str(e))
    except ValueError:
        raise ValueError("Ambiguous command. Invalid amount.")
    return out
