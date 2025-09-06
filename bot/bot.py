import os, json, logging, re, shlex
from datetime import datetime
from typing import List
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("expanses-tracker-tbot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Comma-separated list of numeric chat IDs allowed to use the bot
ALLOWED = {
    int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip().isdigit()
}

CATEGORIES: List[str] = [
    "Food",
    "Gifts",
    "Health/medical",
    "Home",
    "Transportation",
    "Personal",
    "Utilities",
    "Travel",
    "Debt",
    "Other",
    "Family",
    "Wardrobe",
    "Investments",
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
        "/whoami – show your chat id\n"
        "/authorized – check authorization status"
    )

async def cmd_whoami(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    await update.message.reply_text(f"Your chat id: `{uid}`", parse_mode="Markdown")

async def cmd_authorized(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    await update.message.reply_text("true" if is_allowed(uid) else "false")

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

    idx = 0
    date_str = ""
    msg_dt = msg.date
    date_token = parts[0]
    date_match = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{4}))?", date_token)
    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = int(date_match.group(3)) if date_match.group(3) else msg_dt.year
        try:
            date_obj = datetime(year, month, day)
            date_str = date_obj.date().isoformat()
            idx = 1
        except ValueError:
            await msg.reply_text("Ambiguous command. Invalid date.")
            return
    else:
        date_str = msg_dt.date().isoformat()

    if len(parts) - idx < 2:
        await msg.reply_text("Ambiguous command. Not enough parameters.")
        return

    amount_str = parts[idx]
    idx += 1

    remaining = parts[idx:]
    if len(remaining) > 3:
        await msg.reply_text("Ambiguous command. Please quote description if it contains spaces.")
        return

    description = remaining[0]
    category = remaining[1] if len(remaining) >= 2 else ""
    type_ = remaining[2] if len(remaining) >= 3 else ""

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
        buttons = [[InlineKeyboardButton(c, callback_data=f"cat:{c}")] for c in CATEGORIES]
        await msg.reply_text("Select category:", reply_markup=InlineKeyboardMarkup(buttons))
        missing = True
    if not type_:
        buttons = [[InlineKeyboardButton(t, callback_data=f"type:{t}")] for t in TYPES]
        await msg.reply_text("Select type:", reply_markup=InlineKeyboardMarkup(buttons))
        missing = True
    if missing:
        return

    await msg.reply_text(json.dumps(entry))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("whoami", cmd_whoami))
    app.add_handler(CommandHandler("authorized", cmd_authorized))
    app.add_handler(CommandHandler("new", cmd_new))
    app.run_polling(allowed_updates=["message"])

if __name__ == "__main__":
    main()

