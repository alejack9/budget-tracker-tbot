import os, logging
from expanses_tracker_tbot.domain.constants import UNDO_GRACE_SECONDS
from expanses_tracker_tbot.tools.message_parser import get_message_args
from expanses_tracker_tbot.data import ExpenseRepository, DatabaseFactory, init_db
from pydantic import BaseModel, ValidationError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("expanses-tracker-tbot")

BOT_TOKEN = os.environ["BOT_TOKEN"]
# Comma-separated list of numeric chat IDs allowed to use the bot
ALLOWED = {
    int(x) for x in os.environ.get("ALLOWED_CHAT_IDS", "").split(",") if x.strip().isdigit()
}

# Initialize database
init_db()

# TODO add reference to entry
class ButtonData(BaseModel):
    type: str
    value: str

def ensure_access_guard(func):
    async def __wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await ensure_access(update):
            return await func(update, context)
    return __wrapper

def is_allowed(chat_id: int) -> bool:
    return (not ALLOWED) or (chat_id in ALLOWED)

async def ensure_access(update: Update) -> bool:
    uid = update.effective_user.id if update.effective_user else 0
    if not is_allowed(uid):
        await update.effective_chat.send_message("⛔ Unauthorized.")
        log.warning("Unauthorized user tried to use the bot: %s", uid)
        return False
    return True

async def cmd_authorized(update: Update, _: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id if update.effective_user else 0
    await update.message.reply_text("true" if is_allowed(uid) else "false")

@ensure_access_guard
async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm your Expense Tracker Bot.\n\n"
        "Send me expenses in this format:\n"
        "- <amount> <description> [category] [type] [date]\n\n"
        "Examples:\n"
        "10 groceries food need\n"
        "25.50 restaurant food want 15/09\n"
        "100/2 shared bill\n\n"
        "Commands:\n"
        "/authorized - check authorization status"
    )

@ensure_access_guard
async def button_cb(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    data = None
    try:
        data = ButtonData.model_validate_json(query.data)
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
@ensure_access_guard
async def generic_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_id = update.effective_message.message_id
    msg = update.effective_message  # message/channel_post/edited_* whichever exists

    if update.edited_message or update.edited_channel_post:
        try:
            arguments = get_message_args(msg.text, msg.edit_date)
        except ValueError as e:
            await msg.reply_text(str(e))
            await msg.reply_text("Entry not updated.")
            return
        # Get chat ID
        chat_id = update.effective_chat.id
        # Update expense in database
        session = DatabaseFactory.get_session()
        try:
            expense = ExpenseRepository.update_expense(
                session=session,
                message_id=msg_id,
                chat_id=chat_id,
                updated_data={
                    "amount": arguments.amount,
                    "description": arguments.description,
                    "type": arguments.type,
                    "category": arguments.category,
                    "date": arguments.date
                }
            )
            if expense:
                await msg.reply_text(
                    f"Expense updated with ID={msg_id} at {msg.edit_date}:\n"
                    f"Amount: {expense.amount}\n"
                    f"Description: {expense.description}\n"
                    f"Type: {expense.type or 'Not specified'}\n"
                    f"Category: {expense.category or 'Not specified'}\n"
                    f"Date: {expense.date.strftime('%Y-%m-%d')}",
                    reply_to_message_id=msg.message_id
                )
            else:
                await msg.reply_text(
                    f"No existing expense found to update.",
                    reply_to_message_id=msg.message_id
                )
        except Exception as e:
            log.error(f"Error updating expense: {str(e)}")
            await msg.reply_text(
                f"Error updating expense: {str(e)}",
                reply_to_message_id=msg.message_id
            )
        finally:
            session.close()

    elif update.message or update.channel_post:
        try:
            arguments = get_message_args(msg.text, msg.date)
        except ValueError as e:
            await msg.reply_text(str(e), reply_to_message_id=msg.message_id)
            return
            
        # Get chat ID
        chat_id = update.effective_chat.id
        
        # Save expense to database
        session = DatabaseFactory.get_session()
        try:
            expense = ExpenseRepository.create_expense(
                session=session,
                expense=arguments,
                message_id=msg_id,
                chat_id=chat_id
            )
            
            await msg.reply_text(
                f"Expense saved with ID={msg_id} at {msg.date}:\n"
                f"Amount: {expense.amount}\n"
                f"Description: {expense.description}\n"
                f"Type: {expense.type or 'Not specified'}\n"
                f"Category: {expense.category or 'Not specified'}\n"
                f"Date: {expense.date.strftime('%Y-%m-%d')}",
                reply_to_message_id=msg.message_id
            )
        except Exception as e:
            log.error(f"Error saving expense: {str(e)}")
            await msg.reply_text(
                    f"Error saving expense: {str(e)}",
                    reply_to_message_id=msg.message_id
                )
        finally:
            session.close()

@ensure_access_guard
async def cmd_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # get message ID of the replied message
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to the message of the expense you want to delete.")
        return
    # get chat ID
    chat_id = update.effective_chat.id
    message_id = update.message.reply_to_message.message_id
    # Delete expense from database
    session = DatabaseFactory.get_session()
    try:
        success = ExpenseRepository.soft_delete_expense(session, message_id, chat_id)
        if not success:
            await update.message.reply_text(f"No expense found with ID={message_id}.")
        
        # Post a short-lived Restore notice with an inline button
        btn = InlineKeyboardButton(
            text="↩️ Restore",
            callback_data=ButtonData(type="restore", value=f"{chat_id}:{message_id}").model_dump_json(),
        )
        notice = await update.message.reply_text(
            f"Deleted. Tap to restore ({UNDO_GRACE_SECONDS}s).",
            reply_markup=InlineKeyboardMarkup([[btn]]),
            reply_to_message_id=message_id,
        )

        # Schedule deletion of the notice after UNDO_GRACE_SECONDS
        context.job_queue.run_once(
            delete_notice_job,
            when=UNDO_GRACE_SECONDS,
            data={"chat_id": notice.chat_id, "message_id": notice.message_id},
            name=f"del_notice_{notice.chat_id}_{notice.message_id}",
        )
    except Exception as e:
        log.error(f"Error deleting expense: {str(e)}")
        update.message.reply_text(f"Error deleting expense: {str(e)}")
    finally:
        session.close()

@ensure_access_guard
async def button_cb(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        data = ButtonData.model_validate_json(query.data)
    except ValidationError:
        log.error("Invalid callback data: %s", query.data)
        return

    if data.type == "restore":
        # value format: "<chat_id>:<message_id>"
        try:
            chat_id_str, msg_id_str = data.value.split(":")
            chat_id = int(chat_id_str)
            target_id = int(msg_id_str)
        except Exception:
            await query.answer("Invalid restore data.", show_alert=True)
            return

        uid = update.effective_user.id if update.effective_user else 0
        session = DatabaseFactory.get_session()
        try:
            restored = ExpenseRepository.restore(session, chat_id=chat_id, message_id=target_id, user_id=uid)
            if restored:
                await query.answer("Restored")
                try:
                    if query.message:
                        await query.message.delete()
                except Exception:
                    pass
            else:
                await query.answer("Restore window expired or not allowed.", show_alert=True)
        except Exception as e:
            log.exception("Restore failed")
            await query.answer(f"Error: {e}", show_alert=True)
        finally:
            session.close()
        return

    # default/fallback (your existing behavior)
    await query.edit_message_text(text=f"Selected {data.type}: {data.value}")

async def delete_notice_job(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data["chat_id"]
    message_id = job.data["message_id"]
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # Fine if it's already gone or not deletable
        log.debug("Notice delete skipped: %s", e)

def main():
    # Initialize database
    log.info("Initializing database...")
    try:
        engine_name = DatabaseFactory.get_engine_name()
        log.info(f"Using database engine: {engine_name}")
    except ValueError as e:
        log.error(f"Database configuration error: {e}")
        raise
    
    # Initialize Telegram bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("authorized", cmd_authorized))
    app.add_handler(CommandHandler("delete", cmd_delete))
    app.add_handler(MessageHandler(~filters.COMMAND, generic_message_handler), group=1)
    app.add_handler(CallbackQueryHandler(button_cb))
    
    log.info("Bot initialized, starting polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
