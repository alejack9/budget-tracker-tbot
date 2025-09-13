
from typing import Literal, Optional
from pydantic import BaseModel

BTN_CALLBACKS = {}

class ButtonDataDto(BaseModel):
    action: str = Literal['delete', 'restore', 'update']
    message_id: int
    chat_id: int
    type: Optional[str] = None
    value: Optional[str] = None
