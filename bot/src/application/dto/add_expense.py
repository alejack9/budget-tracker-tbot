from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.entities.expense import Expense

@dataclass(slots=True)
class AddExpenseInput:
    msg_id: int
    chat_id: int
    user_id: int
    amount: float
    description: str
    type: Optional[str]
    category: Optional[str]
    date: datetime
    created_at: datetime
    updated_at: datetime

@dataclass(slots=True)
class AddExpenseOutput:
    expense: Expense
