from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ExpenseDto(BaseModel):
    """Model representing the arguments extracted from a message."""
    amount: float
    description: str
    type: Optional[str] = None
    category: Optional[str] = None
    date: datetime
    deleted_at: Optional[datetime] = None
