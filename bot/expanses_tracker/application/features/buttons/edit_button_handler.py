"""Handler for the "edit" button in the expense editing feature."""
import logging
from telegram import CallbackQuery, Update
from telegram.ext import ContextTypes
from expanses_tracker.application.models.button_data_dto import ButtonDataDto
from expanses_tracker.application.utils.decorators import button_callback

log = logging.getLogger(__name__)

@button_callback("edit")
async def edit_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the "edit" button press."""
    await query.edit_message_text(text=f"Selected {data.type}: {data.value}")
