from datetime import datetime
import re
import shlex
from typing import Optional

from expanses_tracker.application.models.expense_dto import ExpenseDto

def __get_message_date__(parts: list[str], default_date: datetime) -> tuple[datetime, list[str]]:
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

def __get_message_domain__(parts: list[str], domain: list[str]) -> tuple[Optional[str], list[str]]:
    """Extract type from the last element of parts if it matches a known type."""
    to_return = None
    if parts and parts[-1].lower() in domain:
        to_return = parts[-1].lower()
        parts.pop() # remove the type part
    return [to_return, parts]

def __get_message_type(parts: list[str]) -> tuple[Optional[str], list[str]]:
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
def get_message_args(text: str, date: datetime) -> ExpenseDto:
    parts = shlex.split(text)
    if not parts:
        raise ValueError("Ambiguous command. Not enough parameters.")
    
    # Extract date
    out_date, parts = __get_message_date__(parts, date)
    
    # Extract type and category
    out_type, parts = __get_message_type(parts)
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
        raise ValueError(str(e))
    except ValueError:
        raise ValueError("Ambiguous command. Invalid amount.")
    
    # Create and return the MessageArgs model instance
    return ExpenseDto(
        amount=out_amount,
        description=out_desc,
        type=out_type,
        category=out_cat,
        date=out_date
    )
