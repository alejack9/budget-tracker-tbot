import logging
from dependency_injector.wiring import Provide
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from src.config.container import Container
from src.config.settings import Settings
import src.interfaces.telegram.commands.messages as messages_module
from .commands import generic_message_handler, start_handler

logging.basicConfig(level=logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)
# TODO fix level to propagate into submodules too
log = logging.getLogger("src")
log.setLevel(logging.DEBUG)

def _application_registration(app):
    """Register application handlers for the Telegram bot."""
    app.add_handler(CommandHandler("start", start_handler))
    # app.add_handler(CommandHandler("delete", delete_command_handler))
    app.add_handler(MessageHandler(~filters.COMMAND, generic_message_handler), group=1)
    # setup_buttons_handlers(app)
    return app

def main(settings: Settings = Provide[Container.settings]):
    """Main function to start the bot."""
    bot_token = settings.bot_token

    # Initialize Telegram bot
    app = ApplicationBuilder().token(bot_token).build()
    app = _application_registration(app)

    log.info("Bot initialized, starting polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    container = Container()
    container.wire(modules=[__name__])
    main()
