"""Buttons feature package."""
import logging
from pydantic_core import ValidationError
from telegram import Message, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from expanses_tracker.application.models.button_data_dto import (
    ButtonCallbacksRegistry,
    ButtonDataDto
)
from expanses_tracker.application.features.buttons.edit_button_handler import (
    edit_category_button_handler
)
from expanses_tracker.application.features.buttons.restore_button_handler import (
    restore_button_handler
)
from expanses_tracker.application.features.buttons.delete_button_handler import (
    delete_button_handler
)
from expanses_tracker.application.utils.decorators import ensure_access_guard

log = logging.getLogger(__name__)

buttons_handlers = [
    delete_button_handler.__name__,
    restore_button_handler.__name__,
    edit_category_button_handler.__name__,
]

def setup_buttons_handlers(app):
    """Setup button handlers by importing them."""
    # The imports above will register the handlers via decorators
    for handler in buttons_handlers:
        log.info("Button handler registered: %s", handler)
    app.add_handler(CallbackQueryHandler(__buttons_handler_router))

@ensure_access_guard
async def __buttons_handler_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None or query.data is None:
        log.error("No callback query or data in update: %s", update)
        return
    await query.answer()
    try:
        data = ButtonDataDto.model_validate_json(query.data)
    except ValidationError:
        log.error("Invalid callback data: %s", query.data)
        return
    if data.action in ButtonCallbacksRegistry.BTN_CALLBACKS:
        handler = ButtonCallbacksRegistry.BTN_CALLBACKS[data.action]
        await handler(query, data, update, context)
    else:
        log.error("Unknown action. Data: %s", data)
        if query.message and isinstance(query.message, Message):
            await query.message.reply_text(f"Unknown action. Data: {data}")

__all__ = [
    setup_buttons_handlers.__name__,
]
