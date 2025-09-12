from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, Float, String, DateTime
from pydantic import BaseModel
from expanses_tracker_tbot.data.database import Base


class ExpenseModel(Base):
    """SQLAlchemy model for an expense in the database"""
    __tablename__ = 'expenses'

    # Database columns
    msg_id = Column(Integer, primary_key=True)  # telegram message id
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    date = Column(DateTime, nullable=False)
    chat_id = Column(Integer, primary_key=True)  # Part of composite primary key with msg_id
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted_at = Column(DateTime, nullable=True)  # Timestamp for soft deletion

    def __repr__(self):
        return (f"<Expense(msg_id={self.msg_id}, chat_id={self.chat_id}, amount={self.amount}, "
                f"description='{self.description}', type='{self.type}', "
                f"category='{self.category}', date='{self.date}', "
                f"created_at='{self.created_at}', updated_at='{self.updated_at}', "
                f"deleted_at='{self.deleted_at}')>")


class ExpenseSchema(BaseModel):
    """Pydantic model for serialization/deserialization of expenses"""
    msg_id: int
    chat_id: int
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
