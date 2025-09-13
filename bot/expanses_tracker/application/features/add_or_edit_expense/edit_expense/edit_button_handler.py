import logging
from telegram import CallbackQuery, Update

from expanses_tracker.application.models.button_data_dto import ButtonDataDto
from expanses_tracker.application.utils.decorators import button_callback

log = logging.getLogger(__name__)

@button_callback("edit")
async def edit_button_handler(query: CallbackQuery, data: ButtonDataDto, update: Update):
    await query.answer()
    data = None
    await query.edit_message_text(text=f"Selected {data.type}: {data.value}")
