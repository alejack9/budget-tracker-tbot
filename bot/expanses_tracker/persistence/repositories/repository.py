from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from expanses_tracker.application.models.expense import ExpenseDto, ExpenseSchema
from expanses_tracker.persistence.configurations.expense_model import ExpenseModel

class ExpenseRepository:
    """Repository class to handle database operations for ExpenseModel"""
    
    @staticmethod
    def create_expense(
        session: Session, 
        expense: ExpenseDto, 
        message_id: int,
        chat_id: int,
        user_id: int
    ) -> ExpenseSchema:
        """
        Create a new expense record in the database
        
        Args:
            session: Database session
            expense: Expense data
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID

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
            chat_id=chat_id,
            user_id=user_id
        )
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        return ExpenseSchema.model_validate(db_expense)
    
    @staticmethod
    def __get_expense_model_by_id(session: Session, message_id: int, chat_id: int, user_id: int, include_deleted: bool = False) -> ExpenseModel | None:
        """
        Get an expense by its message ID, chat ID and user ID
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            include_deleted: Whether to include soft-deleted expenses
            
        Returns:
            ExpenseModel if found, None otherwise
        """
        q = session.query(ExpenseModel).filter(
            ExpenseModel.msg_id == message_id,
            ExpenseModel.chat_id == chat_id,
            ExpenseModel.user_id == user_id
        )
        if not include_deleted:
            q = q.filter(ExpenseModel.deleted_at.is_(None))
        to_return = q.first()
        return to_return

    @staticmethod
    def get_expense_by_id(session: Session, message_id: int, chat_id: int, user_id: int, include_deleted: bool = False) -> Optional[ExpenseSchema]:
        """
        Get an expense by its message ID, chat ID and user ID
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            include_deleted: Whether to include soft-deleted expenses
            
        Returns:
            ExpenseSchema if found, None otherwise
        """
        to_return = ExpenseRepository.__get_expense_model_by_id(
            session, message_id, chat_id, user_id, include_deleted=include_deleted
        )
        return None if to_return is None else ExpenseSchema.model_validate(to_return)

    @staticmethod
    def update_expense(
        session: Session,
        updated_expense: ExpenseSchema
    ) -> Optional[ExpenseSchema]:
        """
        Update an expense record
        
        Args:
            session: Database session
            updated_expense: ExpenseModel instance containing new field values
            
        Returns:
            Updated ExpenseSchema if found, None otherwise
        """
        db_expense = ExpenseRepository.__get_expense_model_by_id(session, updated_expense.msg_id, updated_expense.chat_id, updated_expense.user_id)
        if not db_expense:
            return None
            
        # Update fields from provided model
        db_expense.amount = updated_expense.amount
        db_expense.description = updated_expense.description
        db_expense.type = updated_expense.type
        db_expense.category = updated_expense.category
        db_expense.date = updated_expense.date
                
        session.commit()
        session.refresh(db_expense)
        return ExpenseSchema.model_validate(db_expense)

    @staticmethod
    def soft_delete(session: Session, message_id: int, chat_id: int, user_id: int) -> bool:
        """Set deleted_at=now if owned by user_id and not already deleted. Return True if changed."""
        exp = ExpenseRepository.__get_expense_model_by_id(session, message_id, chat_id, user_id)
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
    def restore(session: Session, chat_id: int, message_id: int, user_id: int, undo_grace_seconds: int) -> bool:
        """
        If deleted_at is within undo_grace_seconds, clear it. Return True if restored.
        
        Args:
            session: Database session
            chat_id: Telegram chat ID
            message_id: Telegram message ID
            user_id: Telegram user ID
            undo_grace_seconds: Time window in seconds during which restoration is allowed
            
        Returns:
            True if restored, False otherwise
        """
        exp = ExpenseRepository.__get_expense_model_by_id(session, message_id, chat_id, user_id, include_deleted=True)
        if not exp or exp.user_id != user_id or exp.deleted_at is None:
            return False
        now = datetime.now(timezone.utc)
        deleted_at = exp.deleted_at
        # Ensure deleted_at is timezone-aware (assume UTC if naive)
        if deleted_at.tzinfo is None:
            deleted_at = deleted_at.replace(tzinfo=timezone.utc)
        passed_time = now - deleted_at
        if passed_time.total_seconds() > undo_grace_seconds:
            return False
        exp.deleted_at = None
        session.commit()
        return True
    
    @staticmethod
    def delete_expense(session: Session, message_id: int, chat_id: int, user_id: int) -> bool:
        """
        Delete an expense record that is still marked as soft deleted.
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID

        Returns:
            True if deleted, False if not found
        """
        db_expense = ExpenseRepository.__get_expense_model_by_id(session, message_id, chat_id, user_id, include_deleted=True)
        if not db_expense:
            return False
        # Skip hard deletion when the expense was restored before the grace window elapsed
        if db_expense.deleted_at is None:
            return False
 
        session.delete(db_expense)
        session.commit()
        return True
