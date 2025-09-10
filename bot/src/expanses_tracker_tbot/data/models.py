from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()


class ExpenseModel(Base):
    """SQLAlchemy model for an expense in the database"""
    __tablename__ = 'expenses'

    # Database columns
    id = Column(Integer, primary_key=True)  # telegram message id, unique per chat
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    date = Column(DateTime, nullable=False)
    chat_id = Column(Integer, nullable=False)  # To ensure uniqueness across chats
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return (f"<Expense(id={self.id}, amount={self.amount}, "
                f"description='{self.description}', type='{self.type}', "
                f"category='{self.category}', date='{self.date}')>")


class ExpenseSchema(BaseModel):
    """Pydantic model for serialization/deserialization of expenses"""
    id: int
    amount: float
    description: str
    type: Optional[str] = None
    category: Optional[str] = None
    date: datetime
    chat_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
