from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.domain.entities.expense import Expense
from src.domain.repositories.expense_repository import ExpenseRepository

from ..models import ExpenseORM

class SqlAlchemyExpenseRepository(ExpenseRepository):
    """SQLAlchemy implementation of ExpenseRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ---------- Mapping helpers ----------

    @staticmethod
    def _to_domain(model: ExpenseORM) -> Expense:
        return Expense(
            msg_id=model.msg_id,
            chat_id=model.chat_id,
            user_id=model.user_id,
            amount=model.amount,
            description=model.description,
            type=model.type,
            category=model.category,
            date=model.date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def _to_orm(expense: Expense) -> ExpenseORM:
        return ExpenseORM(
            msg_id=expense.msg_id,
            chat_id=expense.chat_id,
            user_id=expense.user_id,
            amount=expense.amount,
            description=expense.description,
            type=expense.type,
            category=expense.category,
            date=expense.date,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
            deleted_at=expense.deleted_at,
        )

    # ---------- Interface implementation ----------

    def create(
        self,
        expense: Expense
    ) -> Expense:
        """
        Create a new expense record in the database
        
        Args:
            session: Database session
            expense: Expense data

        Returns:
            The created Expense instance
        """
        orm_obj = self._to_orm(expense)
        self._session.add(orm_obj)
        self._session.commit()
        self._session.refresh(orm_obj)
        return self._to_domain(orm_obj)

    def __get_by_id(self, message_id: int, chat_id: int, user_id: int, include_deleted: bool = False) -> ExpenseORM | None:
        """
        Get an outcome by its message ID, chat ID and user ID
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            include_deleted: Whether to include soft-deleted outcomes
            
        Returns:
            ExpenseORM if found, None otherwise
        """
        q = self._session.query(ExpenseORM).filter(
            ExpenseORM.msg_id == message_id,
            ExpenseORM.chat_id == chat_id,
            ExpenseORM.user_id == user_id
        )
        if not include_deleted:
            q = q.filter(ExpenseORM.deleted_at.is_(None))
        to_return = q.first()
        return to_return

    def get_by_id(
        self,
        message_id: int,
        chat_id: int,
        user_id: int,
        include_deleted: bool = False
    ) -> Optional[Expense]:
        """
        Get an outcome by its message ID, chat ID and user ID
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            include_deleted: Whether to include soft-deleted outcomes
            
        Returns:
            OutcomeSchema if found, None otherwise
        """
        to_return = self.__get_by_id(
            message_id, chat_id, user_id, include_deleted=include_deleted
        )
        return None if to_return is None else self._to_domain(to_return)

    def update(
        self,
        updated_obj: Expense
    ) -> Optional[Expense]:
        """
        Update an outcome record
        
        Args:
            session: Database session
            updated_outcome: OutcomeModel instance containing new field values
            
        Returns:
            Updated OutcomeSchema if found, None otherwise
        """
        db_outcome = self.__get_by_id(updated_obj.msg_id, updated_obj.chat_id, updated_obj.user_id)
        if not db_outcome:
            return None
        
        # Update fields from provided model
        db_outcome.amount = updated_obj.amount
        db_outcome.description = updated_obj.description
        db_outcome.type = updated_obj.type
        db_outcome.category = updated_obj.category
        db_outcome.date = updated_obj.date
                
        self._session.commit()
        self._session.refresh(db_outcome)
        return self._to_domain(db_outcome)
    
    def delete(
        self,
        message_id: int,
        chat_id: int,
        user_id: int,
        hard_delete: bool = False
    ) -> bool:
        """Set deleted_at=now if owned by user_id and not already deleted. Return True if changed."""
        exp = self.__get_by_id(message_id, chat_id, user_id, include_deleted=not hard_delete)
        if not exp:
            return False
        if exp.user_id != user_id:
            return False
        if exp.deleted_at is not None:
            return False
        if not hard_delete:
            exp.deleted_at = datetime.now(tz=timezone.utc)
            self._session.commit()
        else:
            self._session.delete(exp)
            self._session.commit()
        return True

    def restore(
        self,
        chat_id: int,
        message_id: int,
        user_id: int,
        undo_grace_seconds: int
    ) -> bool:
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
        exp = self.__get_by_id(message_id, chat_id, user_id, include_deleted=True)
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
        self._session.commit()
        return True
