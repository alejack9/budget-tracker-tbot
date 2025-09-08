import os, json, logging, re, shlex
from typing import List
from expanses_tracker_tbot.message_parser import get_message_args
from pydantic import BaseModel, ValidationError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("expanses-tracker-tbot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Comma-separated list of numeric chat IDs allowed to use the bot
ALLOWED = {
    int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip().isdigit()
}

# TODO add reference to entry
class QueryData(BaseModel):
    type: str
    value: str

def is_allowed(chat_id: int) -> bool:
    return (not ALLOWED) or (chat_id in ALLOWED)

async def ensure_access(update: Update) -> bool:
    uid = update.effective_user.id if update.effective_user else 0
    if not is_allowed(uid):
        await update.effective_chat.send_message("⛔ Unauthorized.")
        log.warning("Unauthorized user tried to use the bot: %s", uid)
        return False
    return True

async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not await ensure_access(update):
        return
    await update.message.reply_text( # TODO: change message
        "Hi! I can restart your Docker service.\n\n"
        "Commands:\n"
        "/whoami - show your chat id\n"
        "/authorized - check authorization status"
    )

async def cmd_authorized(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    await update.message.reply_text("true" if is_allowed(uid) else "false")

async def button_cb(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    data = None
    try:
        data = QueryData.model_validate_json(query.data)
    except ValidationError:
        log.error("Invalid callback data: %s", query.data)
        return

    await query.edit_message_text(text=f"Selected {data.type}: {data.value}")

# valid strings formats:
# - 10 spesa casa food need -> type: need, category: food, amount: 10, description: spesa casa
# - 10.5 spesa casa food need -> type: need, category: food, amount: 10.5, description: spesa casa
# - 10.50 spesa casa food need -> type: need, category: food, amount: 10.50, description: spesa casa
# - 10 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa
# - 10/2 spesa -> type: TBD (via buttons), category: TBD (via buttons), amount: 5 (10/2), description: spesa
# - 10 spesa casa 21/05 -> type: TBD (via buttons), category: TBD (via buttons), amount: 10, description: spesa casa, date: 21/05/current_year
# - 10 spesa casa food need 21/05 -> type: need, category: food, amount: 10, description: spesa casa, date: 21/05/current_year
async def non_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_id = update.effective_message.message_id
    msg = update.effective_message  # message/channel_post/edited_* whichever exists

    if update.edited_message or update.edited_channel_post:
        # TODO handle edit
        await msg.reply_text(
            f"EDIT of message_id={msg_id} at {msg.edit_date}. Not implemented yet."
        )
    elif update.message or update.channel_post:
        arguments = get_message_args(msg.text, msg.date)
        

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("authorized", cmd_authorized))
    app.add_handler(MessageHandler(~filters.COMMAND, non_command), group=1)
    # app.add_handler(CommandHandler("new", cmd_new)) # TODO to set
    app.add_handler(CallbackQueryHandler(button_cb))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
