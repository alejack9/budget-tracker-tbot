"""Utility decorators for access control and button handling."""

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from expanses_tracker.application.models.button_data_dto import ButtonActions, ButtonCallbacksRegistry

log = logging.getLogger(__name__)

# Comma-separated list of numeric chat IDs allowed to use the bot
ALLOWED = {
    int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip().isdigit()
}

# Decorator to guard handlers with access control
def ensure_access_guard(func):
    """Decorator to ensure that only authorized users can access the decorated handler."""
    async def __ensure_access(update: Update) -> bool:
        uid = update.effective_user.id if update.effective_user else 0
        if not (not ALLOWED or uid in ALLOWED):
            if effective_chat := update.effective_chat:
                await effective_chat.send_message("⛔ Unauthorized.")
            else:
                log.error("No effective chat found in update.")
            log.warning("Unauthorized user tried to use the bot: %s", uid)
            return False
        return True

    async def __wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await __ensure_access(update):
            return await func(update, context)
    return __wrapper

def button_callback(action: ButtonActions):
    """Decorator to register a button callback action."""
    def decorator(func):
        ButtonCallbacksRegistry.add_callback(action, func)
        return func
    return decorator
