from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities.expense import Expense


class ExpenseRepository(ABC):
    """Port for persisting and retrieving expenses."""

    @abstractmethod
    def create(
        self,
        expense: Expense
    ) -> Expense:
        """Create a new expense record in the database."""
        raise NotImplementedError
    
    @abstractmethod
    def get_by_id(
        self,
        message_id: int,
        chat_id: int,
        user_id: int,
        include_deleted: bool = False
    ) -> Optional[Expense]:
        """Get an expense by its message ID, chat ID and user ID."""
        raise NotImplementedError
    
    @abstractmethod
    def update(
        self,
        updated_obj: Expense
    ) -> Optional[Expense]:
        """Update an existing expense record in the database."""
        raise NotImplementedError
    
    @abstractmethod
    def delete(
        self,
        message_id: int,
        chat_id: int,
        user_id: int,
        hard_delete: bool = False
    ) -> bool:
        """Set deleted_at=now if owned by user_id and not already deleted. Return True if changed. If hard_delete=True, hard delete."""
        raise NotImplementedError
    
    @abstractmethod
    def restore(
        self,
        chat_id: int,
        message_id: int,
        user_id: int,
        undo_grace_seconds: int
    ) -> bool:
        """If deleted_at is within undo_grace_seconds, clear it. Return True if restored."""
        raise NotImplementedError
