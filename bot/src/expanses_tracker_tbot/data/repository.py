from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from expanses_tracker_tbot.domain.constants import UNDO_GRACE_SECONDS
from sqlalchemy.orm import Session

from expanses_tracker_tbot.data.database import DatabaseFactory
from expanses_tracker_tbot.data.models import ExpenseModel
from expanses_tracker_tbot.tools.message_parser import Expense


class ExpenseRepository:
    """Repository class to handle database operations for ExpenseModel"""
    
    @staticmethod
    def create_expense(
        session: Session, 
        expense: Expense, 
        message_id: int,
        chat_id: int
    ) -> ExpenseModel:
        """
        Create a new expense record in the database
        
        Args:
            session: Database session
            expense: Expense data
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            
        Returns:
            The created ExpenseModel instance
        """
        db_expense = ExpenseModel(
            msg_id=message_id,
            amount=expense.amount,
            description=expense.description,
            type=expense.type,
            category=expense.category,
            date=expense.date,
            chat_id=chat_id
        )
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        return db_expense
    
    @staticmethod
    def get_expense_by_id(session: Session, message_id: int, chat_id: int, include_deleted: bool = False) -> Optional[ExpenseModel]:
        """
        Get an expense by its message ID and chat ID
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            
        Returns:
            ExpenseModel if found, None otherwise
        """
        q = session.query(ExpenseModel).filter(
            ExpenseModel.msg_id == message_id,
            ExpenseModel.chat_id == chat_id
        )
        if not include_deleted:
            q = q.filter(Expense.deleted_at.is_(None))
        return q.first()

    @staticmethod
    def update_expense(
        session: Session, 
        message_id: int, 
        chat_id: int, 
        updated_data: Dict[str, Any]
    ) -> Optional[ExpenseModel]:
        """
        Update an expense record
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            updated_data: Dictionary with fields to update
            
        Returns:
            Updated ExpenseModel if found, None otherwise
        """
        db_expense = ExpenseRepository.get_expense_by_id(session, message_id, chat_id)
        if not db_expense:
            return None
            
        # Update fields
        for key, value in updated_data.items():
            if hasattr(db_expense, key):
                setattr(db_expense, key, value)
                
        session.commit()
        session.refresh(db_expense)
        return db_expense

    @staticmethod
    def soft_delete(session, chat_id: int, message_id: int, user_id: int) -> bool:
        """Set deleted_at=now if owned by user_id and not already deleted. Return True if changed."""
        exp = ExpenseRepository.get_expense_by_id(session, message_id, chat_id)
        if not exp:
            return False
        if exp.user_id != user_id:
            return False
        if exp.deleted_at is not None:
            return False
        exp.deleted_at = datetime.now(tz=timezone.utc)
        session.commit()
        return True

    @staticmethod
    def restore(session, chat_id: int, message_id: int, user_id: int) -> bool:
        """If deleted_at is within UNDO_GRACE_SECONDS, clear it. Return True if restored."""
        exp = ExpenseRepository.get_expense_by_id(session, message_id, chat_id)
        if not exp or exp.user_id != user_id or exp.deleted_at is None:
            return False
        now = datetime.now(timezone.utc)
        if (now - exp.deleted_at).total_seconds() > UNDO_GRACE_SECONDS:
            return False
        exp.deleted_at = None
        session.commit()
        return True
    
    @staticmethod
    def delete_expense(session: Session, message_id: int, chat_id: int) -> bool:
        """
        Delete an expense record
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            
        Returns:
            True if deleted, False if not found
        """
        db_expense = ExpenseRepository.get_expense_by_id(session, message_id, chat_id)
        if not db_expense:
            return False
            
        session.delete(db_expense)
        session.commit()
        return True
    
    @staticmethod
    def get_all_expenses(session: Session, chat_id: int) -> List[ExpenseModel]:
        """
        Get all expenses for a chat
        
        Args:
            session: Database session
            chat_id: Telegram chat ID
            
        Returns:
            List of ExpenseModel instances
        """
        return session.query(ExpenseModel).filter(
            ExpenseModel.chat_id == chat_id
        ).order_by(ExpenseModel.date.desc()).all()
