"""Utility decorators for access control and button handling."""

import logging
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import Settings

log = logging.getLogger(__name__)

async def _ensure_access(
    update: Update,
    settings: Settings,
) -> bool:
    uid = update.effective_user.id if update.effective_user else 0
    if not (not settings.allowed_chat_ids or uid in settings.allowed_chat_ids):
        if effective_chat := update.effective_chat:
            await effective_chat.send_message("⛔ Unauthorized.")
        else:
            log.error("No effective chat found in update.")
        log.warning("Unauthorized user tried to use the bot: %s", uid)
        return False
    return True

# Decorator to guard handlers with access control
def ensure_access_guard(func):
    """Decorator to ensure that only authorized users can access the decorated handler."""

    @wraps(func)
    async def __wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        settings: Settings,
    ):
        if await _ensure_access(update, settings=settings):
            return await func(update, context)

    return __wrapper
