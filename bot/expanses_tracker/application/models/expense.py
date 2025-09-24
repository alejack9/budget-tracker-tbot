"""Data Transfer Object for expense details in the expense tracker bot."""
from dataclasses import dataclass
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

@dataclass
class ExpenseSchema(BaseModel):
    """Pydantic model for serialization/deserialization of expenses"""
    msg_id: int
    chat_id: int
    user_id: int
    amount: float
    description: str
    type: Optional[str] = None
    category: Optional[str] = None
    date: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
