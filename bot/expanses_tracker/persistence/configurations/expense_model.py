from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, Float, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from expanses_tracker.persistence.configurations.base import Base

class ExpenseModel(Base):
    """SQLAlchemy model for an expense in the database"""
    __tablename__ = 'expenses'

    # Database columns
    msg_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # telegram message id
    chat_id: Mapped[int] = mapped_column(Integer, primary_key=True) # telegram chat id
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # telegram user id
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # Timestamp for soft deletion

    def __repr__(self):
        return (f"<Expense(msg_id={self.msg_id}, chat_id={self.chat_id}, user_id={self.user_id}, "
                f"amount={self.amount}, description='{self.description}', type='{self.type}', "
                f"category='{self.category}', date='{self.date}', "
                f"created_at='{self.created_at}', updated_at='{self.updated_at}', "
                f"deleted_at='{self.deleted_at}')>")
