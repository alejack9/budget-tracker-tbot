"""Data Transfer Object for button data in the expense tracker bot."""
from typing import Literal, Optional
from pydantic import BaseModel


class ButtonCallbacksRegistry:
    """Registry for button callback actions."""
    BTN_CALLBACKS = {}
    @staticmethod
    def add_callback(action: str, func):
        """Register a button callback action."""
        ButtonCallbacksRegistry.BTN_CALLBACKS[action] = func

class ButtonDataDto(BaseModel):
    """Data Transfer Object for button data."""
    action: str = Literal['delete', 'restore', 'category', 'type']
    message_id: int
    chat_id: int
    value: Optional[str] = None
