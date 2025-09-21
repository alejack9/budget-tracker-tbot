from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from expanses_tracker.application.models.outcome import OutcomeDto, OutcomeSchema
from expanses_tracker.persistence.configurations.outcome_model import OutcomeModel

class OutcomeRepository:
    """Repository class to handle database operations for OutcomeModel"""
    
    @staticmethod
    def create_outcome(
        session: Session,
        outcome: OutcomeDto,
        message_id: int,
        chat_id: int,
        user_id: int
    ) -> OutcomeSchema:
        """
        Create a new outcome record in the database
        
        Args:
            session: Database session
            outcome: Outcome data
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID

        Returns:
            The created OutcomeModel instance
        """
        db_outcome = OutcomeModel(
            msg_id=message_id,
            amount=outcome.amount,
            description=outcome.description,
            type=outcome.type,
            category=outcome.category,
            date=outcome.date,
            chat_id=chat_id,
            user_id=user_id
        )
        session.add(db_outcome)
        session.commit()
        session.refresh(db_outcome)
        return OutcomeSchema.model_validate(db_outcome)
    
    @staticmethod
    def __get_outcome_model_by_id(session: Session, message_id: int, chat_id: int, user_id: int, include_deleted: bool = False) -> OutcomeModel | None:
        """
        Get an outcome by its message ID, chat ID and user ID
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID
            include_deleted: Whether to include soft-deleted outcomes
            
        Returns:
            OutcomeModel if found, None otherwise
        """
        q = session.query(OutcomeModel).filter(
            OutcomeModel.msg_id == message_id,
            OutcomeModel.chat_id == chat_id,
            OutcomeModel.user_id == user_id
        )
        if not include_deleted:
            q = q.filter(OutcomeModel.deleted_at.is_(None))
        to_return = q.first()
        return to_return

    @staticmethod
    def get_outcome_by_id(session: Session, message_id: int, chat_id: int, user_id: int, include_deleted: bool = False) -> Optional[OutcomeSchema]:
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
        to_return = OutcomeRepository.__get_outcome_model_by_id(
            session, message_id, chat_id, user_id, include_deleted=include_deleted
        )
        return None if to_return is None else OutcomeSchema.model_validate(to_return)

    @staticmethod
    def update_outcome(
        session: Session,
        updated_outcome: OutcomeSchema
    ) -> Optional[OutcomeSchema]:
        """
        Update an outcome record
        
        Args:
            session: Database session
            updated_outcome: OutcomeModel instance containing new field values
            
        Returns:
            Updated OutcomeSchema if found, None otherwise
        """
        db_outcome = OutcomeRepository.__get_outcome_model_by_id(session, updated_outcome.msg_id, updated_outcome.chat_id, updated_outcome.user_id)
        if not db_outcome:
            return None
            
        # Update fields from provided model
        db_outcome.amount = updated_outcome.amount
        db_outcome.description = updated_outcome.description
        db_outcome.type = updated_outcome.type
        db_outcome.category = updated_outcome.category
        db_outcome.date = updated_outcome.date
                
        session.commit()
        session.refresh(db_outcome)
        return OutcomeSchema.model_validate(db_outcome)

    @staticmethod
    def soft_delete(session: Session, message_id: int, chat_id: int, user_id: int) -> bool:
        """Set deleted_at=now if owned by user_id and not already deleted. Return True if changed."""
        exp = OutcomeRepository.__get_outcome_model_by_id(session, message_id, chat_id, user_id)
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
        exp = OutcomeRepository.__get_outcome_model_by_id(session, message_id, chat_id, user_id, include_deleted=True)
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
    def delete_outcome(session: Session, message_id: int, chat_id: int, user_id: int) -> bool:
        """
        Delete an outcome record that is still marked as soft deleted.
        
        Args:
            session: Database session
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            user_id: Telegram user ID

        Returns:
            True if deleted, False if not found
        """
        db_outcome = OutcomeRepository.__get_outcome_model_by_id(session, message_id, chat_id, user_id, include_deleted=True)
        if not db_outcome:
            return False
        # Skip hard deletion when the outcome was restored before the grace window elapsed
        if db_outcome.deleted_at is None:
            return False
 
        session.delete(db_outcome)
        session.commit()
        return True
