from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Expense:
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
    deleted_at: Optional[datetime]
