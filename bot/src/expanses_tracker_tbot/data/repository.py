from datetime import datetime
from typing import List, Optional, Dict, Any
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
            id=message_id,
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
    def get_expense_by_id(session: Session, message_id: int, chat_id: int) -> Optional[ExpenseModel]:
        """
        Get an expense by its message ID and chat ID
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            
        Returns:
            ExpenseModel if found, None otherwise
        """
        return session.query(ExpenseModel).filter(
            ExpenseModel.id == message_id,
            ExpenseModel.chat_id == chat_id
        ).first()
    
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
