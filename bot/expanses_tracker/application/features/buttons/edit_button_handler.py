"""Handler for the "edit" button in the expense editing feature."""
import logging
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes
from expanses_tracker.application.models.button_data_dto import ButtonActions, ButtonDataDto
from expanses_tracker.application.utils.decorators import button_callback

log = logging.getLogger(__name__)

@button_callback(ButtonActions.CATEGORY)
async def edit_category_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the "edit category" button press."""
    # TODO ask for the category with buttons. When clicked, update the value of the category for the entry.
    log.debug("Query: %s", query)
    log.debug("Update: %s", update)
    log.debug("Context: %s", context)
    # await query.edit_message_text(text=f"Selected category: {data.value}")

@button_callback(ButtonActions.TYPE)
async def edit_type_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the "edit type" button press."""
    # TODO ask for the type with buttons. When clicked, update the value of the type for the entry.
    log.debug("Query: %s", query)
    log.debug("Update: %s", update)
    log.debug("Context: %s", context)
    # await query.edit_message_text(text=f"Selected type: {data.value}")
