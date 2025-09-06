import os, json, logging, re, shlex
from datetime import datetime
from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("expanses-tracker-tbot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Comma-separated list of numeric chat IDs allowed to use the bot
ALLOWED = {
    int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip().isdigit()
}

CATEGORIES: List[str] = [
    "food",
    "gifts",
    "health",
    "home",
    "transportation",
    "personal",
    "utilities",
    "travel",
    "debt",
    "other",
    "family",
    "wardrobe",
    "investments",
]

TYPES: List[str] = ["need", "want", "goal"]

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
    await update.message.reply_text(
        "Hi! I can restart your Docker service.\n\n"
        "Commands:\n"
        "/whoami - show your chat id\n"
        "/authorized - check authorization status"
    )

async def cmd_whoami(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    await update.message.reply_text(f"Your chat id: `{uid}`", parse_mode="Markdown")

async def cmd_authorized(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    await update.message.reply_text("true" if is_allowed(uid) else "false")

# TODO add reference to entry
class QueryData(BaseModel):
    type: str
    value: str

async def cmd_new(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not await ensure_access(update):
        return

    msg = update.message
    if not msg or not msg.text:
        return

    try:
        parts = shlex.split(msg.text)
    except ValueError:
        await msg.reply_text("Ambiguous command. Please check your quotes.")
        return

    if parts and parts[0].startswith("/new"):
        parts = parts[1:]

    if not parts:
        await msg.reply_text("Ambiguous command. Not enough parameters.")
        return

    date_str = ""
    msg_dt = msg.date
    date_token = parts[0]
    date_match_candidate = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", date_token) # match d/m or d/m/yyyy
    if date_match_candidate:
        day = int(date_match_candidate.group(1))
        month = int(date_match_candidate.group(2))
        year = int(date_match_candidate.group(3)) if date_match_candidate.group(3) else msg_dt.year
        try:
            date_obj = datetime(year, month, day)
            date_str = date_obj.date().isoformat()
            parts = parts[1:]
        except ValueError:
            await msg.reply_text("Ambiguous command. Invalid date.")
            return
    else:
        date_str = msg_dt.date().isoformat()

    # if the remaining parts are less than 2, we can't have amount and description
    if len(parts) < 2:
        await msg.reply_text("Ambiguous command. Not enough parameters.")
        return

    amount_str = parts[0]

    remaining = parts[1:]
    if len(remaining) > 3:
        await msg.reply_text("Ambiguous command. Please quote description if it contains spaces.")
        return

    description = remaining[0]
    category = remaining[1] if len(remaining) >= 2 else ""
    # if lowercase category is not in CATEGORIES, we treat it as ""
    if category and category.lower() not in CATEGORIES:
        category = ""
    type_ = remaining[2] if len(remaining) >= 3 else ""
    # if lowercase type_ is not in TYPES, we treat it as ""
    if type_ and type_.lower() not in TYPES:
        type_ = ""

    try:
        amount = float(amount_str)
    except ValueError:
        await msg.reply_text("Ambiguous command. Amount must be a number.")
        return

    entry = {
        "date": date_str,
        "amount": amount,
        "description": description,
        "category": category,
        "type": type_,
    }
    missing = False
    if not category:
        buttons = [[InlineKeyboardButton(c, callback_data=QueryData(type="category", value=c).model_dump_json())] for c in CATEGORIES]
        await msg.reply_text("Select category:", reply_markup=InlineKeyboardMarkup(buttons))
        missing = True
    if not type_:
        buttons = [[InlineKeyboardButton(t, callback_data=QueryData(type="type", value=t).model_dump_json())] for t in TYPES]
        await msg.reply_text("Select type:", reply_markup=InlineKeyboardMarkup(buttons))
        missing = True
    if missing:
        return

    await msg.reply_text(json.dumps(entry))

async def button(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
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

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("authorized", cmd_authorized))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()