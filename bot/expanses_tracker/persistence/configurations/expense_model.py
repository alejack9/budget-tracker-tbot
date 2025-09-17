from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime
from expanses_tracker.persistence.configurations.base import Base

class ExpenseModel(Base):
    """SQLAlchemy model for an expense in the database"""
    __tablename__ = 'expenses'

    # Database columns
    msg_id = Column(Integer, primary_key=True)  # telegram message id
    chat_id = Column(Integer, primary_key=True) # telegram chat id
    user_id = Column(Integer, primary_key=True)  # telegram user id
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    type = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted_at = Column(DateTime, nullable=True)  # Timestamp for soft deletion

    def __repr__(self):
        return (f"<Expense(msg_id={self.msg_id}, chat_id={self.chat_id}, user_id={self.user_id}, "
                f"amount={self.amount}, description='{self.description}', type='{self.type}', "
                f"category='{self.category}', date='{self.date}', "
                f"created_at='{self.created_at}', updated_at='{self.updated_at}', "
                f"deleted_at='{self.deleted_at}')>")
