import os, logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.expanses_tracker.application.models.button_data_dto import BTN_CALLBACKS

log = logging.getLogger(__name__)

# Comma-separated list of numeric chat IDs allowed to use the bot
ALLOWED = { int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip().isdigit() }

# Decorator to guard handlers with access control
def ensure_access_guard(func):
    async def __ensure_access(update: Update) -> bool:
        uid = update.effective_user.id if update.effective_user else 0
        if not (not ALLOWED or uid in ALLOWED):
            await update.effective_chat.send_message("⛔ Unauthorized.")
            log.warning("Unauthorized user tried to use the bot: %s", uid)
            return False
        return True

    async def __wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await __ensure_access(update):
            return await func(update, context)
    return __wrapper

def button_callback(action: str):
    def decorator(func):
        func._button_action = action
        BTN_CALLBACKS[action] = func
        return func
    return decorator
