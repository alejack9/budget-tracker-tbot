"""Data Transfer Object for button data in the outcome tracker bot."""
from typing import Optional
from pydantic import BaseModel
from enum import Enum

class BUTTON_ACTIONS(Enum):
    DELETE = 'delete'
    RESTORE = 'restore'
    CATEGORY = 'category'
    TYPE = 'type'

class ButtonCallbacksRegistry:
    """Registry for button callback actions."""
    BTN_CALLBACKS = {}
    @staticmethod
    def add_callback(action: BUTTON_ACTIONS, func):
        """Register a button callback action."""
        if action in ButtonCallbacksRegistry.BTN_CALLBACKS:
            raise ValueError(f"Callback for action {action} is already registered.")
        ButtonCallbacksRegistry.BTN_CALLBACKS[action] = func

class ButtonDataDto(BaseModel):
    """Data Transfer Object for button data."""
    action: BUTTON_ACTIONS
    message_id: int
    chat_id: int
    value: Optional[str] = None
